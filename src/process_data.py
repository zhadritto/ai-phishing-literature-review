import json
import csv
import numpy as np
import os

np.random.seed(42)

RAW = "data/raw/test_run.jsonl"
OUT = "data/processed/metrics_summary.csv"

os.makedirs("data/processed", exist_ok=True)
rows = [json.loads(l) for l in open(RAW, encoding="utf-8")]

def bootstrap_ci(vals, n_boot=2000):
    vals = np.array(vals)
    boot = [np.random.choice(vals, size=len(vals), replace=True).mean() for _ in range(n_boot)]
    return np.percentile(boot, [2.5, 97.5])

results = []

# 1. Recall для фишинга
phish = [r for r in rows if r["email_type"] == "ai_phishing"]
phish_correct = [r["correct"] for r in phish]
recall = np.mean(phish_correct)
ci_lo, ci_hi = bootstrap_ci(phish_correct)
results.append(("Detection Recall", "AI Phishing", round(recall, 3), round(ci_lo, 3), round(ci_hi, 3), len(phish)))

# 2. FPR для настоящих писем
legit = [r for r in rows if r["email_type"] == "legitimate"]
legit_wrong = [1 if r["predicted_label"] == "phishing" else 0 for r in legit]
fpr = np.mean(legit_wrong)
ci_lo, ci_hi = bootstrap_ci(legit_wrong)
results.append(("False Positive Rate", "Legitimate", round(fpr, 3), round(ci_lo, 3), round(ci_hi, 3), len(legit)))

# Guardrail
guardrail_passed = "TRUE" if fpr <= 0.20 else "FALSE"
results.append(("Guardrail (FPR <= 0.20)", "Legitimate", guardrail_passed, "", "", ""))

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["Metric", "Group", "Value", "CI_Lower", "CI_Upper", "N_Responses"])
    w.writerows(results)

print(f"✅ Метрики сохранены в {OUT}")
print("-" * 40)
for r in results:
    print(r)
