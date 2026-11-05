from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


# --------------------------------------------------
# PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT / "data" / "processed"
OUTPUT_DIR = ROOT / "reports" / "figures"

LONG_DATA = DATA_DIR / "student_responses_long.csv"
DEMOGRAPHICS_DATA = DATA_DIR / "survey_demographics_summary.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

sns.set_theme(style="whitegrid", palette="colorblind")

plt.rcParams.update({
    "font.size": 11,
    "figure.dpi": 150,
    "savefig.dpi": 300,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
})


def save_figure(fig, filename):
    """Save a figure in PNG and PDF formats."""

    fig.tight_layout()

    fig.savefig(
        OUTPUT_DIR / f"{filename}.png",
        bbox_inches="tight"
    )

    fig.savefig(
        OUTPUT_DIR / f"{filename}.pdf",
        bbox_inches="tight"
    )

    plt.close(fig)

    print(f"Saved: {filename}.png and {filename}.pdf")


# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

if not LONG_DATA.exists():
    raise FileNotFoundError(
        f"Missing file: {LONG_DATA}. "
        "Run src/process_survey.py first."
    )

if not DEMOGRAPHICS_DATA.exists():
    raise FileNotFoundError(
        f"Missing file: {DEMOGRAPHICS_DATA}. "
        "Run src/process_survey.py first."
    )

df = pd.read_csv(LONG_DATA)
demographics = pd.read_csv(DEMOGRAPHICS_DATA)

required_columns = {
    "participant_id",
    "email_id",
    "predicted_label",
    "true_label",
}

missing_columns = required_columns - set(df.columns)

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

df = df.dropna(
    subset=["predicted_label", "true_label"]
).copy()

if df.empty:
    raise ValueError("No valid classifications found.")

df["is_correct"] = (
    df["predicted_label"] == df["true_label"]
)

print("SURVEY VISUALIZATION")
print("--------------------")
print("Participants:", df["participant_id"].nunique())
print("Email questions:", df["email_id"].nunique())
print("Valid classifications:", len(df))
print("Overall accuracy:", round(df["is_correct"].mean() * 100, 2), "%")


# --------------------------------------------------
# FIGURE 1: CONFUSION MATRIX
# --------------------------------------------------

labels = ["legitimate", "phishing"]

confusion_matrix = pd.crosstab(
    df["true_label"],
    df["predicted_label"]
).reindex(
    index=labels,
    columns=labels,
    fill_value=0
)

fig, ax = plt.subplots(figsize=(7, 5))

sns.heatmap(
    confusion_matrix,
    annot=True,
    fmt="d",
    cmap="Blues",
    linewidths=0.5,
    cbar=True,
    ax=ax
)

ax.set_title("Confusion Matrix")
ax.set_xlabel("Predicted Label")
ax.set_ylabel("True Label")

save_figure(fig, "survey_confusion_matrix")


# --------------------------------------------------
# FIGURE 2: ACCURACY BY EMAIL
# --------------------------------------------------

email_accuracy = (
    df.groupby("email_id")
    .agg(
        accuracy=("is_correct", "mean"),
        true_label=("true_label", "first"),
        responses=("is_correct", "count")
    )
    .reset_index()
)

email_accuracy["accuracy"] *= 100

fig, ax = plt.subplots(figsize=(11, 6))

sns.barplot(
    data=email_accuracy,
    x="email_id",
    y="accuracy",
    hue="true_label",
    order=sorted(email_accuracy["email_id"].unique()),
    ax=ax
)

ax.axhline(
    df["is_correct"].mean() * 100,
    linestyle="--",
    color="black",
    label="Overall accuracy"
)

ax.set_title("Classification Accuracy by Email")
ax.set_xlabel("Email")
ax.set_ylabel("Accuracy (%)")
ax.set_ylim(0, 105)
ax.tick_params(axis="x", rotation=45)
ax.legend(title="True label")

save_figure(fig, "survey_accuracy_by_email")


# --------------------------------------------------
# FIGURE 3: PARTICIPANT PERFORMANCE
# --------------------------------------------------

participant_scores = (
    df.groupby("participant_id")
    .agg(
        correct_answers=("is_correct", "sum"),
        total_answers=("is_correct", "count")
    )
    .reset_index()
)

fig, ax = plt.subplots(figsize=(8, 5))

sns.histplot(
    data=participant_scores,
    x="correct_answers",
    bins=range(0, 14),
    discrete=True,
    color="steelblue",
    ax=ax
)

ax.set_title("Participant Performance Distribution")
ax.set_xlabel("Correct Answers (out of 12)")
ax.set_ylabel("Number of Participants")
ax.set_xticks(range(0, 13))

save_figure(fig, "survey_participant_performance")


# --------------------------------------------------
# FIGURE 4: PARTICIPANT DEMOGRAPHICS
# --------------------------------------------------

demographic_variables = [
    ("age_group", "Age Group"),
    ("cyber_knowledge", "Self-Assessed Cybersecurity Knowledge"),
    ("phishing_experience", "Previous Phishing Experience"),
    ("first_indicator", "First Phishing Indicator"),
]

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

for ax, (variable, title) in zip(
    axes.flatten(),
    demographic_variables
):
    subset = demographics[
        demographics["variable"] == variable
    ].copy()

    if subset.empty:
        ax.set_visible(False)
        continue

    subset = subset.sort_values("count", ascending=True)

    sns.barplot(
        data=subset,
        x="count",
        y="category",
        color="steelblue",
        ax=ax
    )

    ax.set_title(title)
    ax.set_xlabel("Number of Participants")
    ax.set_ylabel("")

    for container in ax.containers:
        ax.bar_label(container, padding=3)

fig.suptitle(
    "Survey Participant Demographics",
    fontsize=16,
    y=1.02
)

save_figure(fig, "survey_demographics")


# --------------------------------------------------
# FINISH
# --------------------------------------------------

print()
print("VISUALIZATION COMPLETED")
print("-----------------------")
print("Figures saved to:", OUTPUT_DIR)
print("Formats: PNG and PDF")
print("Number of figures: 4")
