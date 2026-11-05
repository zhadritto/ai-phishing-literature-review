import csv
import json
import os

INPUT_CSV = "data/raw/responses.csv"
OUTPUT_JSONL = "data/raw/test_run.jsonl"

EMAIL_MAP = {
    "4. Является ли это письмо фишинговым?":  "ai_phishing",
    "5. Является ли это письмо фишинговым?":  "legitimate",
    "6. Является ли это письмо фишинговым?":  "ai_phishing",
    "7. Является ли это письмо фишинговым?":  "legitimate",
    "8. Является ли это письмо фишинговым?":  "ai_phishing",
    "9. Является ли это письмо фишинговым?":  "legitimate",
    "10. Является ли это письмо фишинговым?": "ai_phishing",
    "11. Является ли это письмо фишинговым?": "legitimate",
    "12. Является ли это письмо фишинговым?": "ai_phishing",
    "13. Является ли это письмо фишинговым?": "legitimate",
    "14. Является ли это письмо фишинговым?": "ai_phishing",
    "15. Является ли это письмо фишинговым?": "legitimate",
}

# Создаем папки на всякий случай
os.makedirs("data/raw", exist_ok=True)

records = []
with open(INPUT_CSV, encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        pid = f"P{i+1:02d}"  # Генерируем ID: P01, P02... P27
        
        for col, true_type in EMAIL_MAP.items():
            raw_ans = row.get(col, "").strip().lower()
            
            if "фишинг" in raw_ans:
                pred = "phishing"
            elif "настоящ" in raw_ans:
                pred = "legitimate"
            else:
                continue  

            is_correct = int(
                (pred == "phishing" and true_type == "ai_phishing") or 
                (pred == "legitimate" and true_type == "legitimate")
            )
            
            records.append({
                "participant_id": pid,
                "email_id": col.split('.')[0], 
                "email_type": true_type,
                "predicted_label": pred,
                "correct": is_correct,
                "cyber_knowledge": row.get("2. Как бы вы оценили свои знания в области кибербезопасности?", ""),
                "phishing_experience": row.get("3. Сталкивались ли вы раньше с фишинговыми письмами или сообщениями?", "")
            })

with open(OUTPUT_JSONL, "w", encoding="utf-8") as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False) + "\n")

print(f"✅ Успешно обработано {len(records)} ответов от {i+1} участников.")
print(f"Файл сохранен: {OUTPUT_JSONL}")
