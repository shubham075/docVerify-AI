import os
import time
import json
import requests


DATASET_DIR = os.path.join(os.path.dirname(__file__), "..", "tests", "fixtures", "test_dataset_100")
MANIFEST_PATH = os.path.join(DATASET_DIR, "manifest.json")
API_URL = "http://127.0.0.1:8000/api/v1/verify"

def main():
    if not os.path.exists(MANIFEST_PATH):
        print(f"Error: Manifest not found at {MANIFEST_PATH}")
        return

    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    print("=" * 70)
    print(f"RUNNING DOCUMENT QUALITY PIPELINE BENCHMARK (100 Test Cases)")
    print("=" * 70)
    print(f"Target Server: {API_URL}")
    print(f"Total Test Documents: {len(manifest)}\n")

    results = []
    correct_count = 0
    start_time_all = time.time()

    # Track classification counts
    confusion = {
        "PASS": {"PASS": 0, "BORDERLINE": 0, "REJECT": 0},
        "BORDERLINE": {"PASS": 0, "BORDERLINE": 0, "REJECT": 0},
        "REJECT": {"PASS": 0, "BORDERLINE": 0, "REJECT": 0},
    }

    category_stats = {}

    for idx, item in enumerate(manifest, start=1):
        file_id = item["id"]
        pipeline = item["pipeline"]
        expected = item["expected_status"]
        category = item["category"]
        desc = item["description"]
        rel_path = item["relative_path"]
        filepath = os.path.join(DATASET_DIR, rel_path)

        if not os.path.exists(filepath):
            print(f"File missing: {filepath}")
            continue

        t0 = time.time()
        try:
            with open(filepath, "rb") as f:
                resp = requests.post(
                    API_URL,
                    files={"file": (item["filename"], f, "image/png")},
                    data={"doc_type": pipeline},
                    timeout=30
                )
            latency_ms = (time.time() - t0) * 1000

            if resp.status_code == 200:
                body = resp.json()
                predicted = body.get("status", "UNKNOWN")
                stages = body.get("stages", {})
                reason = body.get("final_reason", "")
            else:
                predicted = "ERROR"
                stages = {}
                reason = f"HTTP {resp.status_code}: {resp.text[:80]}"
        except Exception as e:
            latency_ms = (time.time() - t0) * 1000
            predicted = "ERROR"
            stages = {}
            reason = str(e)

        is_correct = (predicted == expected)
        if is_correct:
            correct_count += 1

        if expected in confusion and predicted in confusion[expected]:
            confusion[expected][predicted] += 1

        # Track category
        if category not in category_stats:
            category_stats[category] = {"total": 0, "correct": 0}
        category_stats[category]["total"] += 1
        if is_correct:
            category_stats[category]["correct"] += 1

        # Sharpness score display
        sharp_score = stages.get("sharpness", {}).get("score", "N/A")
        if isinstance(sharp_score, (int, float)):
            sharp_score = f"{sharp_score:.1f}"

        # Status icon
        status_icon = "[PASS]" if is_correct else "[FAIL]"

        print(f"[{idx:03d}/100] {file_id:<8} ({pipeline:<11}) Expected: {expected:<10} Actual: {predicted:<10} Score: {str(sharp_score):<7} {latency_ms:>5.0f}ms {status_icon}")

        results.append({
            "id": file_id,
            "filename": item["filename"],
            "pipeline": pipeline,
            "category": category,
            "expected_status": expected,
            "predicted_status": predicted,
            "is_correct": is_correct,
            "latency_ms": round(latency_ms, 2),
            "final_reason": reason,
            "stages": stages
        })

    total_time = time.time() - start_time_all
    accuracy_pct = (correct_count / len(manifest)) * 100

    print("\n" + "=" * 70)
    print("BENCHMARK EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Total Test Cases:    {len(manifest)}")
    print(f"Accurate Decisions:  {correct_count} / {len(manifest)} ({accuracy_pct:.1f}%)")
    print(f"Total Elapsed Time:  {total_time:.2f}s (Avg {total_time/len(manifest)*1000:.1f} ms/file)")

    # Confusion Matrix
    print("\nConfusion Matrix (Rows: Expected, Columns: Predicted):")
    print("            Pred PASS  Pred BORDERLINE  Pred REJECT")
    print(f"Exp PASS       {confusion['PASS']['PASS']:>6}         {confusion['PASS']['BORDERLINE']:>6}       {confusion['PASS']['REJECT']:>6}")
    print(f"Exp BORDERLINE {confusion['BORDERLINE']['PASS']:>6}         {confusion['BORDERLINE']['BORDERLINE']:>6}       {confusion['BORDERLINE']['REJECT']:>6}")
    print(f"Exp REJECT     {confusion['REJECT']['PASS']:>6}         {confusion['REJECT']['BORDERLINE']:>6}       {confusion['REJECT']['REJECT']:>6}")

    # Category Accuracy
    print("\nAccuracy by Distortion / Quality Category:")
    for cat, data in category_stats.items():
        pct = (data['correct'] / data['total']) * 100
        print(f"  - {cat:<18}: {data['correct']:>2}/{data['total']:>2} ({pct:>5.1f}%)")

    # Reject / Blur Precision & Recall
    true_rejects = confusion["REJECT"]["REJECT"]
    false_rejects = confusion["PASS"]["REJECT"] + confusion["BORDERLINE"]["REJECT"]
    missed_rejects = confusion["REJECT"]["PASS"] + confusion["REJECT"]["BORDERLINE"]

    precision_reject = (true_rejects / (true_rejects + false_rejects)) * 100 if (true_rejects + false_rejects) > 0 else 0
    recall_reject = (true_rejects / (true_rejects + missed_rejects)) * 100 if (true_rejects + missed_rejects) > 0 else 0
    f1_reject = (2 * precision_reject * recall_reject) / (precision_reject + recall_reject) if (precision_reject + recall_reject) > 0 else 0

    print(f"\nBlur & Defect Detection Metrics:")
    print(f"  - Defect Detection Recall:    {recall_reject:.1f}%")
    print(f"  - Defect Detection Precision: {precision_reject:.1f}%")
    print(f"  - Defect Detection F1-Score:  {f1_reject:.1f}%")

    # Output JSON Report
    report = {
        "total_documents": len(manifest),
        "overall_accuracy_pct": round(accuracy_pct, 2),
        "total_time_seconds": round(total_time, 2),
        "avg_latency_ms": round(total_time / len(manifest) * 1000, 2),
        "confusion_matrix": confusion,
        "category_performance": category_stats,
        "defect_metrics": {
            "recall_pct": round(recall_reject, 2),
            "precision_pct": round(precision_reject, 2),
            "f1_pct": round(f1_reject, 2)
        },
        "results": results
    }

    report_path = os.path.join(DATASET_DIR, "benchmark_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\n[OK] Detailed JSON report saved to: {report_path}")

if __name__ == "__main__":
    main()
