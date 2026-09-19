import os
import io
import json
import urllib.request
import cv2
import numpy as np
from PIL import Image
import pyarrow.parquet as pq

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "test_dataset_100")
GENERAL_DIR = os.path.join(OUTPUT_DIR, "general_doc")
ID_DIR = os.path.join(OUTPUT_DIR, "id_passport")

os.makedirs(GENERAL_DIR, exist_ok=True)
os.makedirs(ID_DIR, exist_ok=True)

# -------------------------------------------------------------
# Distortion Helper Functions
# -------------------------------------------------------------

def apply_defocus_blur(img: np.ndarray, radius: int = 15) -> np.ndarray:
    """Simulates camera lens defocus blur using a disc/circular filter."""
    kernel = np.zeros((radius * 2 + 1, radius * 2 + 1), dtype=np.float32)
    cv2.circle(kernel, (radius, radius), radius, 1.0, -1)
    kernel /= kernel.sum()
    return cv2.filter2D(img, -1, kernel)

def apply_motion_blur(img: np.ndarray, size: int = 25, angle: float = 45.0) -> np.ndarray:
    """Simulates camera shake / motion blur with directional kernel."""
    M = cv2.getRotationMatrix2D((size / 2, size / 2), angle, 1.0)
    kernel = np.diag(np.ones(size, dtype=np.float32))
    kernel = cv2.warpAffine(kernel, M, (size, size))
    kernel /= kernel.sum()
    return cv2.filter2D(img, -1, kernel)

def apply_glare_spot(img: np.ndarray, center_pct=(0.5, 0.4), radius_pct=0.18) -> np.ndarray:
    """Simulates bright camera flash reflection / specular glare on laminated ID."""
    res = img.copy()
    h, w = res.shape[:2]
    cx = int(w * center_pct[0])
    cy = int(h * center_pct[1])
    radius = int(min(h, w) * radius_pct)
    # Bright white glare
    cv2.circle(res, (cx, cy), radius, (255, 255, 255), -1)
    return cv2.GaussianBlur(res, (31, 31), 0)

def apply_borderline_blur(img: np.ndarray, sigma: float = 1.6) -> np.ndarray:
    """Simulates slight, threshold-edge softness (borderline)."""
    return cv2.GaussianBlur(img, (0, 0), sigma)

def create_synthetic_id_card(id_num: int, name: str, nationality: str = "UTOPIA") -> np.ndarray:
    """Generates realistic ID document image with MRZ zone, photo frame, and text fields."""
    # Standard ID-1 aspect ratio at high resolution (1600 x 1010)
    w, h = 1600, 1010
    card = np.ones((h, w, 3), dtype=np.uint8) * 215

    # Card background subtle pattern/border
    cv2.rectangle(card, (20, 20), (w - 20, h - 20), (180, 195, 210), 8)
    cv2.rectangle(card, (30, 30), (w - 30, h - 30), (220, 225, 230), -1)

    # Header
    cv2.rectangle(card, (30, 30), (w - 30, 150), (45, 85, 150), -1)
    cv2.putText(card, f"IDENTITY CARD / CARTE D'IDENTITE - {nationality}", (60, 95), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (255, 255, 255), 3)
    cv2.putText(card, "OFFICIAL RECOGNITION DOCUMENT", (60, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (210, 225, 245), 2)

    # Photo Box
    cv2.rectangle(card, (70, 200), (450, 680), (160, 170, 180), 3)
    cv2.rectangle(card, (75, 205), (445, 675), (195, 200, 205), -1)
    cv2.putText(card, "PORTRAIT PHOTO", (140, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (110, 110, 120), 2)

    # Identity Fields
    fields = [
        ("SURNAME / NOM:", name.split()[-1].upper()),
        ("GIVEN NAMES / PRENOMS:", name.split()[0].upper()),
        ("NATIONALITY / NATIONALITE:", nationality),
        ("DATE OF BIRTH / DATE NAISSANCE:", "14 APR 1988"),
        ("DOCUMENT NO / NO DU DOCUMENT:", f"P{id_num:06d}89A"),
        ("EXPIRY DATE / DATE D'EXPIRATION:", "28 OCT 2032"),
    ]

    y_pos = 230
    for label, val in fields:
        cv2.putText(card, label, (500, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (90, 95, 105), 2)
        cv2.putText(card, val, (500, y_pos + 40), cv2.FONT_HERSHEY_SIMPLEX, 1.05, (15, 20, 30), 2)
        y_pos += 75

    # MRZ (Machine Readable Zone) at the bottom (Standard 2-line TD3/TD1 format)
    cv2.rectangle(card, (50, 750), (w - 50, h - 50), (195, 200, 205), -1)
    line1 = f"I<{nationality[:3]}P{id_num:06d}89A<<<<<<<<<<<<<<"
    line2 = f"8804147M3210284{nationality[:3]}<<<<<<<<<<<2"
    cv2.putText(card, line1, (70, 830), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (10, 15, 25), 3)
    cv2.putText(card, line2, (70, 910), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (10, 15, 25), 3)

    return card

def create_synthetic_general_doc(doc_id: int, title: str, doc_type: str = "INVOICE") -> np.ndarray:
    """Generates high-contrast, structured business/legal document page."""
    w, h = 1200, 1600
    doc = np.ones((h, w, 3), dtype=np.uint8) * 210

    # Document Header
    cv2.putText(doc, f"{doc_type} #{10000 + doc_id}", (80, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.4, (20, 30, 45), 3)
    cv2.putText(doc, f"Date: 2026-03-15   Ref: DOC-VERIFY-{doc_id:04d}", (80, 165), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (90, 95, 105), 2)
    cv2.line(doc, (80, 190), (w - 80, 190), (160, 165, 175), 2)

    # Title & Subtitle
    cv2.putText(doc, title, (80, 250), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (15, 20, 30), 2)

    # Paragraphs / Line Items
    y = 320
    for i in range(16):
        cv2.putText(
            doc,
            f"Item {i+1:02d}: Specification verification line item documenting quality benchmarks and validation criteria.",
            (80, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (40, 45, 55),
            2
        )
        y += 55

    # Table section
    cv2.rectangle(doc, (80, y + 20), (w - 80, y + 220), (225, 230, 235), -1)
    cv2.rectangle(doc, (80, y + 20), (w - 80, y + 220), (160, 165, 175), 2)
    cv2.putText(doc, "Total Amount Due: $14,850.00 USD", (120, y + 80), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (20, 25, 35), 2)
    cv2.putText(doc, "Payment Terms: Net 30 days upon receipt", (120, y + 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (70, 75, 85), 2)
    cv2.putText(doc, "Authorized Signature: Verified Document Agent", (120, y + 180), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (70, 75, 85), 2)

    return doc

# -------------------------------------------------------------
# Main Generation Logic
# -------------------------------------------------------------

def main():
    print("Preparing 100-document evaluation benchmark dataset...")
    manifest = []

    # 1. Fetch real scanned base documents from RVL-CDIP demo parquet
    print("Streaming real scanned document seeds from RVL-CDIP...")
    real_scanned_images = []
    try:
        url = "https://huggingface.co/datasets/nielsr/rvl-cdip-demo/resolve/main/data/train-00000-of-00001.parquet"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp:
            table = pq.read_table(io.BytesIO(resp.read()))
            for i in range(table.num_rows):
                img_bytes = table["image"][i].as_py()["bytes"]
                pil_img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                np_img = np.array(pil_img)
                # Ensure minimum resolution meets sanity requirements (1500px long edge)
                h, w = np_img.shape[:2]
                scale = 1600.0 / max(h, w)
                np_img = cv2.resize(np_img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)
                # Normalize mean luma to fit standard document sanity range [40, 220]
                np_img = np.clip(np_img.astype(np.float32) * 0.88, 0, 212).astype(np.uint8)
                real_scanned_images.append(np_img)
        print(f"Loaded {len(real_scanned_images)} real scanned base images.")
    except Exception as e:
        print(f"Warning: Could not fetch RVL-CDIP parquet: {e}. Using synthetic generators.")

    # ---------------------------------------------------------
    # SUITE A: 50 General Documents
    # ---------------------------------------------------------
    titles = [
        "Annual Financial Audit Summary Statement",
        "Commercial Lease Agreement Terms & Conditions",
        "Vendor Procurement & Purchase Order Invoice",
        "Health Care Benefit & Insurance Claim Form",
        "Corporate Tax Return Schedule A Filing",
        "Independent Contractor Service Agreement",
        "Software Licensing & Maintenance Contract",
        "International Commercial Bill of Lading",
        "Quarterly Shareholder Investment Report",
        "Quality Control Compliance Inspection Certificate"
    ]

    print("Generating 50 General Documents...")
    for idx in range(1, 51):
        filename = f"general_doc_{idx:03d}.png"
        filepath = os.path.join(GENERAL_DIR, filename)

        # Base image
        if real_scanned_images and idx <= len(real_scanned_images):
            base = real_scanned_images[idx - 1].copy()
        else:
            title = titles[(idx - 1) % len(titles)]
            base = create_synthetic_general_doc(idx, title)

        if idx <= 25:
            # 1 to 25: Sharp / Clean -> Expected PASS
            expected = "PASS"
            category = "sharp"
            desc = "Sharp, high-resolution original scanned document with clear text"
            out_img = base
        elif idx <= 40:
            # 26 to 40: Blurry -> Expected REJECT
            expected = "REJECT"
            category = "blurry"
            if idx % 2 == 0:
                out_img = apply_defocus_blur(base, radius=16)
                desc = "Severe out-of-focus defocus blur"
            else:
                out_img = apply_motion_blur(base, size=31, angle=35.0)
                desc = "Heavy linear motion camera blur"
        else:
            # 41 to 50: Borderline & Edge cases
            if idx <= 45:
                expected = "BORDERLINE"
                category = "borderline"
                out_img = apply_borderline_blur(base, sigma=1.05)
                desc = "Mild optical softness near borderline threshold"
            else:
                expected = "REJECT"
                category = "sanity_failure"
                if idx == 46 or idx == 47:
                    # Low resolution
                    out_img = cv2.resize(base, (600, 800), interpolation=cv2.INTER_AREA)
                    desc = "Resolution too low (long edge < 1500px)"
                elif idx == 48:
                    # Extremely dark
                    out_img = (base * 0.12).astype(np.uint8)
                    desc = "Brightness too low (< 40 mean luma)"
                else:
                    # Extremely washed out
                    out_img = np.clip(base.astype(np.int32) + 120, 0, 255).astype(np.uint8)
                    desc = "Brightness too high (> 220 mean luma)"

        cv2.imwrite(filepath, out_img)
        manifest.append({
            "id": f"GEN_{idx:03d}",
            "filename": filename,
            "relative_path": os.path.relpath(filepath, OUTPUT_DIR),
            "pipeline": "general",
            "expected_status": expected,
            "category": category,
            "description": desc
        })

    # ---------------------------------------------------------
    # SUITE B: 50 ID & Passport Documents
    # ---------------------------------------------------------
    names = [
        "Emma Watson", "Alexander Dupont", "Carlos Silva", "Elena Rostova",
        "Liam O'Connor", "Mei-Ling Chen", "Tariq Mansoor", "Katarina Novak",
        "Amara Okafor", "David Johansson"
    ]
    countries = ["UTOPIA", "CAN", "DEU", "FRA", "GBR", "AUS", "JPN", "BRA"]

    print("Generating 50 ID & Passport Documents...")
    for idx in range(1, 51):
        filename = f"id_passport_{idx:03d}.png"
        filepath = os.path.join(ID_DIR, filename)

        name = names[(idx - 1) % len(names)]
        country = countries[(idx - 1) % len(countries)]
        base = create_synthetic_id_card(idx, name, country)

        if idx <= 20:
            # 1 to 20: Sharp ID cards -> Expected PASS
            expected = "PASS"
            category = "sharp"
            desc = "Crisp, fully legible ID card with clear MRZ and photo portrait"
            out_img = base
        elif idx <= 35:
            # 21 to 35: Blurry IDs -> Expected REJECT
            expected = "REJECT"
            category = "blurry"
            if idx % 2 == 0:
                out_img = apply_defocus_blur(base, radius=18)
                desc = "Severe camera defocus blur on ID card"
            else:
                out_img = apply_motion_blur(base, size=35, angle=60.0)
                desc = "Hand-shake motion blur across ID MRZ zone"
        elif idx <= 45:
            # 36 to 45: Glare / Specular reflection -> Expected REJECT
            expected = "REJECT"
            category = "glare"
            out_img = apply_glare_spot(base, center_pct=(0.55, 0.45), radius_pct=0.22)
            desc = "Excessive specular flash glare on plastic laminate (>1.5% area)"
        else:
            # 46 to 50: Borderline & Edge cases
            if idx <= 48:
                expected = "BORDERLINE"
                category = "borderline"
                out_img = apply_borderline_blur(base, sigma=1.05)
                desc = "Borderline sharpness score requiring OCR tiebreaker"
            else:
                expected = "REJECT"
                category = "sanity_failure"
                out_img = cv2.resize(base, (800, 505), interpolation=cv2.INTER_AREA)
                desc = "Resolution too low for ID (long edge < 1200px)"

        cv2.imwrite(filepath, out_img)
        manifest.append({
            "id": f"ID_{idx:03d}",
            "filename": filename,
            "relative_path": os.path.relpath(filepath, OUTPUT_DIR),
            "pipeline": "id_passport",
            "expected_status": expected,
            "category": category,
            "description": desc
        })

    # Save manifest
    manifest_path = os.path.join(OUTPUT_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n[OK] Successfully created 100 test documents in: {OUTPUT_DIR}")
    print(f"Manifest written to: {manifest_path}")

if __name__ == "__main__":
    main()
