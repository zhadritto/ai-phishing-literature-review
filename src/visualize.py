import json
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

sns.set_theme(style="whitegrid", palette="colorblind")
plt.rcParams.update({'font.size': 12, 'figure.dpi': 300})

os.makedirs("reports/figures", exist_ok=True)
rows = [json.loads(l) for l in open("data/raw/test_run.jsonl", encoding="utf-8")]

groups = ["Низкие", "Средние", "Высокие"]
recalls = []
errors = []

for g in groups:
    subset = [r["correct"] for r in rows if r["email_type"] == "ai_phishing" and g in r["cyber_knowledge"]]
    if subset:
        recalls.append(np.mean(subset) * 100)
        errors.append(np.std(subset) / np.sqrt(len(subset)) * 196) # 95% CI
    else:
        recalls.append(0)
        errors.append(0)

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(groups, recalls, yerr=errors, capsize=5, color='#0072B2', edgecolor='black', alpha=0.8)
ax.set_ylabel("Detection Recall (%)")
ax.set_xlabel("Self-rated Cyber Knowledge")
ax.set_ylim(0, 110)
ax.set_title("AI Phishing Detection by Cyber Knowledge")
plt.tight_layout()
plt.savefig("reports/figures/fig1_latency_vs_load.pdf")
plt.savefig("reports/figures/fig1_latency_vs_load.png", dpi=300)
plt.close()

participant_scores = {}
for r in rows:
    pid = r["participant_id"]
    if pid not in participant_scores:
        participant_scores[pid] = 0
    participant_scores[pid] += r["correct"]

scores = list(participant_scores.values())

fig, ax = plt.subplots(figsize=(6, 5))
sns.boxplot(y=scores, color='#009E73', width=0.4, ax=ax)
sns.stripplot(y=scores, color='black', alpha=0.5, jitter=True, ax=ax)
ax.set_ylabel("Number of Correct Answers (out of 12)")
ax.set_xlabel("Participants (N=27)")
ax.set_title("Participant Performance Distribution")
plt.tight_layout()
plt.savefig("reports/figures/fig2_distribution_boxplot.pdf")
plt.savefig("reports/figures/fig2_distribution_boxplot.png", dpi=300)
plt.close()

print("✅ Графики сохранены в reports/figures/ (форматы .pdf и .png)")
