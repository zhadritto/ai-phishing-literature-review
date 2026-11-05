
import json
import csv
import os
import numpy as np

np.random.seed(42)

RAW = "data/processed/responses.jsonl"
OUT = "data/processed/metrics_summary.csv"

os.makedirs("data/processed", exist_ok=True)

with open(RAW, encoding="utf-8") as f:
    rows = [json.loads(line) for line in f if line.strip()]

def participant_bootstrap(data, n_boot=5000):
    participants = list(set(r["participant_id"] for r in data))
    values = []

    for _ in range(n_boot):
        sampled = np.random.choice(participants, len(participants), replace=True)
        sampled_rows = [
            r for pid in sampled
            for r in data if r["participant_id"] == pid
        ]
        values.append(np.mean([r["correct"] for r in sampled_rows]))

    return np.percentile(values, [2.5, 97.5])

results = []

for email_type in ["ai_phishing", "legitimate"]:
    subset = [r for r in rows if r["email_type"] == email_type]

    if not subset:
        continue

    score = np.mean([r["correct"] for r in subset])
    ci_low, ci_high = participant_bootstrap(subset)

    results.append([
        "Detection Rate",
        email_type,
        round(score, 3),
        round(ci_low, 3),
        round(ci_high, 3),
        len(set(r["participant_id"] for r in subset))
    ])

with open(OUT, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Metric", "Group", "Value",
        "CI_Lower", "CI_Upper", "N_Participants"
    ])
    writer.writerows(results)

print("Metrics saved:", OUT)
for result in results:
    print(result)
