
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ANSWER_KEY = ROOT / "data" / "metadata" / "email_answer_key.csv"


def test_answer_key_has_12_emails():
    df = pd.read_csv(ANSWER_KEY)

    assert len(df) == 12
    assert df["email_id"].nunique() == 12


def test_phishing_and_legitimate_balance():
    df = pd.read_csv(ANSWER_KEY)

    assert (df["true_label"] == "phishing").sum() == 6
    assert (df["true_label"] == "legitimate").sum() == 6


def test_all_emails_are_ai_generated():
    df = pd.read_csv(ANSWER_KEY)

    assert (df["email_source"] == "ai_generated").all()


def test_phishing_email_ids():
    df = pd.read_csv(ANSWER_KEY)

    phishing_ids = set(
        df.loc[df["true_label"] == "phishing", "email_id"]
    )

    assert phishing_ids == {
        "email_01", "email_03", "email_05",
        "email_07", "email_09", "email_11"
    }


def test_legitimate_email_ids():
    df = pd.read_csv(ANSWER_KEY)

    legitimate_ids = set(
        df.loc[df["true_label"] == "legitimate", "email_id"]
    )

    assert legitimate_ids == {
        "email_02", "email_04", "email_06",
        "email_08", "email_10", "email_12"
    }
