import re
from typing import Dict, Any, List, Optional

class OCREntityExtractor:
    """
    Extracts structured entities (MRZ, dates, document numbers, emails, phone numbers, amounts)
    from OCR raw text.
    """
    
    # Common date formats: YYYY-MM-DD, DD/MM/YYYY, DD.MM.YYYY, DD-MMM-YYYY
    DATE_REGEX = re.compile(
        r'\b(?:\d{4}[-/.]\d{2}[-/.]\d{2}|\d{2}[-/.]\d{2}[-/.]\d{4}|\d{2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4})\b',
        re.IGNORECASE
    )
    
    # Common email pattern
    EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    
    # Common phone pattern (international / domestic)
    PHONE_REGEX = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b')
    
    # Currency / Amount pattern: e.g. $1,250.00, €45.99, 1250.50
    AMOUNT_REGEX = re.compile(r'(?:[\$\€\£\¥]\s*)?\b\d{1,3}(?:,\d{3})*(?:\.\d{2})\b')
    
    # Document number pattern: alphanumeric, 6 to 12 chars
    DOC_NUM_REGEX = re.compile(r'\b(?:No[.:]?\s*|ID[.:]?\s*|Passport[.:]?\s*)?([A-Z0-9]{6,12})\b', re.IGNORECASE)

    @classmethod
    def parse_mrz(cls, text: str) -> Optional[Dict[str, Any]]:
        """
        Detects and parses Machine Readable Zone (MRZ) according to ICAO Doc 9303.
        Supports TD3 (Passports, 2 lines x 44 chars) and TD1 (ID Cards, 3 lines x 30 chars).
        """
        lines = [line.strip().replace(" ", "") for line in text.split('\n') if line.strip()]
        
        # Filter lines that look like MRZ characters (mostly capital letters, numbers, and '<')
        mrz_candidates = []
        for line in lines:
            if len(line) >= 28 and line.count('<') >= 2:
                # Clean up OCR noise in MRZ
                clean_line = re.sub(r'[^A-Z0-9<]', '', line.upper())
                if len(clean_line) >= 28:
                    mrz_candidates.append(clean_line)

        # Check TD3 format: 2 lines with length ~44
        for i in range(len(mrz_candidates) - 1):
            line1 = mrz_candidates[i]
            line2 = mrz_candidates[i+1]
            if 42 <= len(line1) <= 46 and 42 <= len(line2) <= 46:
                doc_type = line1[0]
                country = line1[2:5].replace('<', '')
                names_part = line1[5:].split('<<')
                surname = names_part[0].replace('<', ' ').strip()
                given_names = names_part[1].replace('<', ' ').strip() if len(names_part) > 1 else ""
                
                doc_num = line2[0:9].replace('<', '')
                nationality = line2[10:13].replace('<', '')
                dob = line2[13:19]
                sex = line2[20] if len(line2) > 20 else ""
                expiry = line2[21:27]

                return {
                    "format": "TD3 (Passport)",
                    "lines": [line1, line2],
                    "document_type": doc_type,
                    "issuing_country": country,
                    "surname": surname,
                    "given_names": given_names,
                    "full_name": f"{given_names} {surname}".strip(),
                    "document_number": doc_num,
                    "nationality": nationality,
                    "date_of_birth": dob,
                    "sex": sex,
                    "expiry_date": expiry
                }

        # Check TD1 format: 3 lines with length ~30
        for i in range(len(mrz_candidates) - 2):
            l1, l2, l3 = mrz_candidates[i], mrz_candidates[i+1], mrz_candidates[i+2]
            if 28 <= len(l1) <= 32 and 28 <= len(l2) <= 32 and 28 <= len(l3) <= 32:
                doc_type = l1[0:2].replace('<', '')
                country = l1[2:5].replace('<', '')
                doc_num = l1[5:14].replace('<', '')
                dob = l2[0:6]
                sex = l2[7] if len(l2) > 7 else ""
                expiry = l2[8:14]
                names = l3.replace('<', ' ').strip()

                return {
                    "format": "TD1 (ID Card)",
                    "lines": [l1, l2, l3],
                    "document_type": doc_type,
                    "issuing_country": country,
                    "document_number": doc_num,
                    "date_of_birth": dob,
                    "sex": sex,
                    "expiry_date": expiry,
                    "full_name": names
                }

        return None

    @classmethod
    def extract_structured_fields(cls, raw_text: str, doc_type: str) -> Dict[str, Any]:
        """
        Extracts entities from raw OCR text according to document type.
        """
        extracted: Dict[str, Any] = {}

        # 1. Dates
        dates = list(set(cls.DATE_REGEX.findall(raw_text)))
        if dates:
            extracted["dates_found"] = dates[:5]

        # 2. Contact details
        emails = list(set(cls.EMAIL_REGEX.findall(raw_text)))
        if emails:
            extracted["emails"] = emails[:3]

        phones = list(set(cls.PHONE_REGEX.findall(raw_text)))
        # Filter out numbers that are too short to be real phones
        valid_phones = [p.strip() for p in phones if sum(c.isdigit() for c in p) >= 7]
        if valid_phones:
            extracted["phones"] = valid_phones[:3]

        # 3. Financial / Invoice fields for General Docs
        if doc_type == "general":
            amounts = list(set(cls.AMOUNT_REGEX.findall(raw_text)))
            if amounts:
                extracted["amounts_found"] = amounts[:5]

            # Look for Invoice / PO identifiers
            inv_match = re.search(r'(?:Invoice|INV|Bill|Account|Order)\s*(?:No|#|Number)?[:\s]*([A-Z0-9-_]{3,20})', raw_text, re.IGNORECASE)
            if inv_match:
                extracted["invoice_number"] = inv_match.group(1).strip()

        # 4. Identity Fields / MRZ for Passports & IDs
        if doc_type == "id_passport":
            mrz_data = cls.parse_mrz(raw_text)
            if mrz_data:
                extracted["mrz"] = mrz_data
                if mrz_data.get("full_name"):
                    extracted["full_name"] = mrz_data["full_name"]
                if mrz_data.get("document_number"):
                    extracted["document_number"] = mrz_data["document_number"]
                if mrz_data.get("date_of_birth"):
                    extracted["date_of_birth"] = mrz_data["date_of_birth"]
                if mrz_data.get("expiry_date"):
                    extracted["expiry_date"] = mrz_data["expiry_date"]

            # Visual Inspection Zone (VIZ) label-based extraction
            surname_match = re.search(r'(?:SURNAME|NOM|LAST\s*NAME)[:\s\n]*([A-Z]{2,30})', raw_text, re.IGNORECASE)
            given_match = re.search(r'(?:GIVEN\s*NAMES|PRENOMS|FIRST\s*NAME)[:\s\n]*([A-Z]{2,30})', raw_text, re.IGNORECASE)
            doc_num_match = re.search(r'(?:DOCUMENT\s*NO|NO\s*DU\s*DOCUMENT|PASSPORT\s*NO|ID\s*NO)[:\s\n]*([A-Z0-9]{6,15})', raw_text, re.IGNORECASE)
            nat_match = re.search(r'(?:NATIONALITY|NATIONALITE)[:\s\n]*([A-Z]{3,30})', raw_text, re.IGNORECASE)

            if surname_match and not extracted.get("surname"):
                extracted["surname"] = surname_match.group(1).strip()
            if given_match and not extracted.get("given_names"):
                extracted["given_names"] = given_match.group(1).strip()
            if surname_match and given_match and not extracted.get("full_name"):
                extracted["full_name"] = f"{given_match.group(1).strip()} {surname_match.group(1).strip()}"
            if doc_num_match and not extracted.get("document_number"):
                extracted["document_number"] = doc_num_match.group(1).strip()
            if nat_match and not extracted.get("nationality"):
                extracted["nationality"] = nat_match.group(1).strip()

            if not extracted.get("document_number"):
                doc_matches = cls.DOC_NUM_REGEX.findall(raw_text)
                if doc_matches:
                    valid_candidates = [m for m in doc_matches if len(m) >= 6 and not m.startswith("ENTITY")]
                    if valid_candidates:
                        extracted["document_number"] = valid_candidates[0]

        return extracted
