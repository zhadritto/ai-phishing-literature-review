
import csv
import json
import os

INPUT_CSV = "data/raw/responses.csv"
OUTPUT_JSONL = "data/processed/responses.jsonl"

EMAIL_MAP = {
    "4. Является ли это письмо фишинговым?": "ai_phishing",
    "5. Является ли это письмо фишинговым?": "legitimate",
    "6. Является ли это письмо фишинговым?": "ai_phishing",
    "7. Является ли это письмо фишинговым?": "legitimate",
    "8. Является ли это письмо фишинговым?": "ai_phishing",
    "9. Является ли это письмо фишинговым?": "legitimate",
    "10. Является ли это письмо фишинговым?": "ai_phishing",
    "11. Является ли это письмо фишинговым?": "legitimate",
    "12. Является ли это письмо фишинговым?": "ai_phishing",
    "13. Является ли это письмо фишинговым?": "legitimate",
    "14. Является ли это письмо фишинговым?": "ai_phishing",
    "15. Является ли это письмо фишинговым?": "legitimate",
}

os.makedirs("data/processed", exist_ok=True)

def parse_answer(answer):
    answer = answer.strip().lower()

    if answer in {"да", "yes"}:
        return "phishing"
    if answer in {"нет", "no"}:
        return "legitimate"

    raise ValueError(f"Unknown answer option: {answer!r}")

records = []

with open(INPUT_CSV, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)

    for i, row in enumerate(reader, start=1):
        for column, true_type in EMAIL_MAP.items():
            if column not in row:
                raise ValueError(f"Missing CSV column: {column}")

            prediction = parse_answer(row[column])

            records.append({
                "participant_id": f"P{i:02d}",
                "email_id": column.split(".")[0],
                "email_type": true_type,
                "predicted_label": prediction,
                "correct": int(
                    (true_type == "ai_phishing" and prediction == "phishing")
                    or (true_type == "legitimate" and prediction == "legitimate")
                ),
                "cyber_knowledge": row.get(
                    "2. Как бы вы оценили свои знания в области кибербезопасности?", ""
                ),
                "phishing_experience": row.get(
                    "3. Сталкивались ли вы раньше с фишинговыми письмами или сообщениями?", ""
                )
            })

with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
    for record in records:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

print(f"Participants: {i if records else 0}")
print(f"Responses: {len(records)}")
print(f"Saved to: {OUTPUT_JSONL}")
