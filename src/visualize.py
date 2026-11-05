
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

required = {
    "participant_id", "email_type", "correct", "cyber_knowledge"
}
missing = required - set(df.columns)

if missing:
    raise ValueError(f"Missing columns: {missing}")

if df.empty:
    raise ValueError("No response data found.")

if not set(df["email_type"].unique()).issubset(
    {"ai_phishing", "human_phishing", "legitimate"}
):
    raise ValueError("Unknown email_type found.")

# Detection recall by phishing authorship
phishing = df[df["email_type"].isin(
    ["ai_phishing", "human_phishing"]
)].copy()

participant_scores = (
    phishing.groupby(["participant_id", "email_type"])["correct"]
    .mean()
    .unstack()
    .dropna(subset=["ai_phishing", "human_phishing"])
)

if participant_scores.empty:
    raise ValueError("No participants have both phishing conditions.")

# Figure 1: Mean participant-level recall with bootstrap CI
rng = np.random.default_rng(SEED)

groups = ["ai_phishing", "human_phishing"]
means = []
lower = []
upper = []

for group in groups:
    values = participant_scores[group].to_numpy()
    boot = np.array([
        rng.choice(values, size=len(values), replace=True).mean()
        for _ in range(N_BOOT)
    ])

    means.append(values.mean() * 100)
    ci = np.percentile(boot, [2.5, 97.5]) * 100
    lower.append(means[-1] - ci[0])
    upper.append(ci[1] - means[-1])

fig, ax = plt.subplots(figsize=(8, 5))
ax.bar(
    ["AI-generated", "Human-written"],
    means,
    yerr=[lower, upper],
    capsize=5
)
ax.set_ylabel("Detection Recall (%)")
ax.set_xlabel("Phishing Email Type")
ax.set_title("Phishing Detection Recall by Email Authorship")
ax.set_ylim(0, 100)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/fig1_detection_recall.png", dpi=300)
plt.savefig(f"{OUTPUT}/fig1_detection_recall.pdf")
plt.close()

# Figure 2: Paired participant-level comparison
fig, ax = plt.subplots(figsize=(8, 5))

for _, row in participant_scores.iterrows():
    ax.plot(
        ["AI-generated", "Human-written"],
        [row["ai_phishing"] * 100, row["human_phishing"] * 100],
        marker="o",
        alpha=0.35
    )

ax.set_ylabel("Detection Recall (%)")
ax.set_xlabel("Phishing Email Type")
ax.set_title("Within-Participant Detection Recall")
ax.set_ylim(0, 100)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/fig2_paired_comparison.png", dpi=300)
plt.savefig(f"{OUTPUT}/fig2_paired_comparison.pdf")
plt.close()

# Figure 3: Participant-level recall by cybersecurity knowledge
knowledge = (
    phishing.groupby(["participant_id", "cyber_knowledge"])["correct"]
    .mean()
    .reset_index()
)

fig, ax = plt.subplots(figsize=(9, 5))
sns.boxplot(
    data=knowledge,
    x="cyber_knowledge",
    y="correct",
    ax=ax
)
sns.stripplot(
    data=knowledge,
    x="cyber_knowledge",
    y="correct",
    color="black",
    alpha=0.5,
    ax=ax
)

ax.set_ylabel("Participant Detection Recall")
ax.set_xlabel("Self-rated Cybersecurity Knowledge")
ax.set_title("Detection Recall by Cybersecurity Knowledge")
ax.set_ylim(0, 1)
ax.tick_params(axis="x", rotation=20)
plt.tight_layout()
plt.savefig(f"{OUTPUT}/fig3_cyber_knowledge.png", dpi=300)
plt.savefig(f"{OUTPUT}/fig3_cyber_knowledge.pdf")
plt.close()

# Paired difference and participant-level bootstrap CI for RQ2
differences = (
    participant_scores["ai_phishing"]
    - participant_scores["human_phishing"]
).to_numpy()

boot_diff = np.array([
    rng.choice(differences, size=len(differences), replace=True).mean()
    for _ in range(N_BOOT)
])

ci_low, ci_high = np.percentile(boot_diff, [2.5, 97.5])

print("RQ2: AI recall - Human recall")
print(f"Difference: {differences.mean():.3f}")
print(f"95% bootstrap CI: [{ci_low:.3f}, {ci_high:.3f}]")
print(f"Participants included: {len(differences)}")
print(f"Figures saved in: {OUTPUT}")
