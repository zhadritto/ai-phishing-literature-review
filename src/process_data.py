
import json
import csv
import os
import numpy as np

RAW = "data/processed/responses.jsonl"
OUT = "data/processed/metrics_summary.csv"
N_BOOT = 5000

rng = np.random.default_rng(42)

with open(RAW, encoding="utf-8") as f:
    rows = [json.loads(line) for line in f if line.strip()]

if not rows:
    raise ValueError("No response data found.")

results = []

def bootstrap_ci(values):
    values = np.asarray(values, dtype=float)
    boot = [
        rng.choice(values, size=len(values), replace=True).mean()
        for _ in range(N_BOOT)
    ]
    return np.percentile(boot, [2.5, 97.5])

participants = sorted(set(r["participant_id"] for r in rows))

for email_type in ["ai_phishing", "legitimate"]:
    participant_scores = []

    for pid in participants:
        subset = [
            r for r in rows
            if r["participant_id"] == pid
            and r["email_type"] == email_type
        ]

        if subset:
            if email_type == "ai_phishing":
                score = np.mean([
                    r["predicted_label"] == "phishing" for r in subset
                ])
                metric = "Detection Recall"
            else:
                score = np.mean([
                    r["predicted_label"] == "phishing" for r in subset
                ])
                metric = "False Positive Rate"

            participant_scores.append(score)

    if participant_scores:
        mean = np.mean(participant_scores)
        ci_low, ci_high = bootstrap_ci(participant_scores)

        results.append([
            metric,
            email_type,
            round(mean, 3),
            round(ci_low, 3),
            round(ci_high, 3),
            len(participant_scores)
        ])

os.makedirs("data/processed", exist_ok=True)

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
