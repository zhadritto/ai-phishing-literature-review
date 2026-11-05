
import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", palette="colorblind")

INPUT = "data/processed/responses.jsonl"
OUTPUT = "reports/figures"
N_BOOT = 5000
SEED = 42

os.makedirs(OUTPUT, exist_ok=True)

with open(INPUT, encoding="utf-8") as f:
    rows = [json.loads(line) for line in f if line.strip()]

df = pd.DataFrame(rows)

required = {"participant_id", "email_type", "correct", "cyber_knowledge"}
missing = required - set(df.columns)

if missing:
    raise ValueError(f"Missing columns: {missing}")

if df.empty:
    raise ValueError("No response data found.")

rng = np.random.default_rng(SEED)

# Participant-level metrics
participant_scores = (
    df.groupby(["participant_id", "email_type"])
    .agg(
        accuracy=("correct", "mean"),
        cyber_knowledge=("cyber_knowledge", "first")
    )
    .reset_index()
)

def bootstrap_ci(values):
    values = np.asarray(values, dtype=float)
    boot = [
        rng.choice(values, size=len(values), replace=True).mean()
        for _ in range(N_BOOT)
    ]
    return np.percentile(boot, [2.5, 97.5])

# Figure 1: AI phishing detection recall
ai = participant_scores[
    participant_scores["email_type"] == "ai_phishing"
]["accuracy"].to_numpy()

if len(ai) == 0:
    raise ValueError("No AI phishing responses found.")

mean_ai = ai.mean() * 100
ci = bootstrap_ci(ai) * 100

fig, ax = plt.subplots(figsize=(7, 5))
ax.bar(
    ["AI-generated phishing"],
    [mean_ai],
    yerr=[[mean_ai - ci[0]], [ci[1] - mean_ai]],
    capsize=5
)
ax.set_ylabel("Detection Recall (%)")
ax.set_title("Detection of AI-Generated Phishing Emails")
ax.set_ylim(0, 100)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/fig1_ai_detection.png", dpi=300)
plt.savefig(f"{OUTPUT}/fig1_ai_detection.pdf")
plt.close()

# Figure 2: False positive rate on legitimate emails
legit = df[df["email_type"] == "legitimate"].copy()
legit["false_positive"] = (
    legit["predicted_label"] == "phishing"
)

fpr_by_participant = (
    legit.groupby("participant_id")["false_positive"]
    .mean()
    .to_numpy()
)

if len(fpr_by_participant) == 0:
    raise ValueError("No legitimate email responses found.")

mean_fpr = fpr_by_participant.mean() * 100
ci = bootstrap_ci(fpr_by_participant) * 100

fig, ax = plt.subplots(figsize=(7, 5))
ax.bar(
    ["Legitimate emails"],
    [mean_fpr],
    yerr=[[mean_fpr - ci[0]], [ci[1] - mean_fpr]],
    capsize=5
)
ax.set_ylabel("False Positive Rate (%)")
ax.set_title("False Positives on Legitimate Emails")
ax.set_ylim(0, 100)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/fig2_false_positive_rate.png", dpi=300)
plt.savefig(f"{OUTPUT}/fig2_false_positive_rate.pdf")
plt.close()

# Figure 3: AI phishing detection by cybersecurity knowledge
ai_data = participant_scores[
    participant_scores["email_type"] == "ai_phishing"
].copy()

fig, ax = plt.subplots(figsize=(9, 5))
sns.stripplot(
    data=ai_data,
    x="cyber_knowledge",
    y="accuracy",
    jitter=True,
    alpha=0.65,
    ax=ax
)
ax.set_ylabel("Participant Detection Recall")
ax.set_xlabel("Self-rated Cybersecurity Knowledge")
ax.set_title("AI Phishing Detection by Cybersecurity Knowledge")
ax.set_ylim(0, 1)
ax.tick_params(axis="x", rotation=20)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/fig3_cyber_knowledge.png", dpi=300)
plt.savefig(f"{OUTPUT}/fig3_cyber_knowledge.pdf")
plt.close()

print("Figures saved in:", OUTPUT)
print("Participants:", df["participant_id"].nunique())
print(f"AI phishing detection recall: {mean_ai:.1f}%")
print(f"Legitimate email false positive rate: {mean_fpr:.1f}%")
