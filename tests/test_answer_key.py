
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

ANSWER_KEY = (
    ROOT / "data" / "metadata" / "email_answer_key.csv"
)


def test_answer_key_has_12_emails():
    df = pd.read_csv(ANSWER_KEY)

    assert len(df) == 12
    assert df["email_id"].nunique() == 12


def test_phishing_and_legitimate_balance():
    df = pd.read_csv(ANSWER_KEY)

    assert (df["true_label"] == "phishing").sum() == 6
    assert (df["true_label"] == "legitimate").sum() == 6


def test_phishing_authorship_groups():
    df = pd.read_csv(ANSWER_KEY)

    phishing = df[df["true_label"] == "phishing"]

    assert (
        phishing["email_source"] == "ai_generated"
    ).sum() == 3

    assert (
        phishing["email_source"] == "human_written"
    ).sum() == 3


def test_legitimate_authorship_is_unknown():
    df = pd.read_csv(ANSWER_KEY)

    legitimate = df[
        df["true_label"] == "legitimate"
    ]

    assert (legitimate["email_source"] == "unknown").all()
