import pandas as pd

from src.process_survey import normalize_answer


def test_phishing_answer():
    assert normalize_answer("Фишинговое письмо") == "phishing"


def test_legitimate_answer():
    assert normalize_answer("Настоящее письмо") == "legitimate"


def test_empty_answer():
    assert pd.isna(normalize_answer(None))


def test_unknown_answer():
    assert pd.isna(normalize_answer("Не знаю"))
