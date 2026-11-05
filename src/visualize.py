
import json
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", palette="colorblind")

INPUT = "data/processed/responses.jsonl"
OUTPUT = "reports/figures"

os.makedirs(OUTPUT, exist_ok=True)

with open(INPUT, encoding="utf-8") as f:
    rows = [json.loads(line) for line in f if line.strip()]

df = pd.DataFrame(rows)

# Figure 1: Detection rate by email type
summary = df.groupby("email_type")["correct"].mean() * 100

fig, ax = plt.subplots(figsize=(8, 5))
summary.plot(kind="bar", ax=ax)
ax.set_ylabel("Correct Detection (%)")
ax.set_xlabel("Email Type")
ax.set_title("Detection Rate by Email Type")
ax.set_ylim(0, 100)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/fig1_detection_rate.png", dpi=300)
plt.savefig(f"{OUTPUT}/fig1_detection_rate.pdf")
plt.close()

# Figure 2: Participant performance
participant_scores = (
    df.groupby(["participant_id", "email_type"])["correct"]
    .mean()
    .reset_index()
)

fig, ax = plt.subplots(figsize=(8, 5))
sns.boxplot(
    data=participant_scores,
    x="email_type",
    y="correct",
    ax=ax
)
sns.stripplot(
    data=participant_scores,
    x="email_type",
    y="correct",
    color="black",
    alpha=0.5,
    ax=ax
)
ax.set_ylabel("Correct Detection Rate")
ax.set_xlabel("Email Type")
ax.set_title("Participant Performance by Email Type")
plt.tight_layout()
plt.savefig(f"{OUTPUT}/fig2_participant_performance.png", dpi=300)
plt.savefig(f"{OUTPUT}/fig2_participant_performance.pdf")
plt.close()

# Figure 3: Self-rated cybersecurity knowledge
knowledge = (
    df.groupby("cyber_knowledge")["correct"]
    .mean()
    .mul(100)
    .reset_index()
)

fig, ax = plt.subplots(figsize=(8, 5))
sns.barplot(
    data=knowledge,
    x="cyber_knowledge",
    y="correct",
    ax=ax
)
ax.set_ylabel("Correct Detection (%)")
ax.set_xlabel("Self-rated Cybersecurity Knowledge")
ax.set_title("Detection Rate by Cybersecurity Knowledge")
ax.tick_params(axis="x", rotation=20)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/fig3_cyber_knowledge.png", dpi=300)
plt.savefig(f"{OUTPUT}/fig3_cyber_knowledge.pdf")
plt.close()

print("Three figures saved in", OUTPUT)
