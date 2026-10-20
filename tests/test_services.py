import json
from typing import Any, Dict, List
import pytest
from src.services import get_profitable_cashback_categories, investment_bank


@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    """Фикстура с тестовыми транзакциями для проверки сервисов."""
    return [
        {"Дата операции": "2020-05-15 12:00:00", "Сумма операции": -1712.0, "Категория": "Супермаркеты"},
        {"Дата операции": "2020-05-20 18:30:00", "Сумма операции": -50.0, "Категория": "Фастфуд"},
        {"Дата операции": "2020-05-21 09:15:00", "Сумма операции": -105.0, "Категория": "Супермаркеты"},
        {"Дата операции": "2020-06-01 10:00:00", "Сумма операции": -300.0, "Категория": "Аптеки"},
        {"Дата операции": "2020-05-22 14:00:00", "Сумма операции": 5000.0, "Категория": "Пополнения"},
    ]


def test_investment_bank_limit_50(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тест инвесткопилки с округлением до 50 рублей."""
    # -1712 округляется до 1750 (копилка +38)
    # -50 делится без остатка (копилка +0)
    # -105 округляется до 150 (копилка +45)
    # Итого должно быть 83.0
    result = investment_bank("2020-05", sample_transactions, 50)
    assert result == 83.0


def test_investment_bank_limit_10(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тест инвесткопилки с округлением до 10 рублей."""
    # -1712 округляется до 1720 (копилка +8)
    # -50 без остатка (копилка +0)
    # -105 округляется до 110 (копилка +5)
    # Итого должно быть 13.0
    result = investment_bank("2020-05", sample_transactions, 10)
    assert result == 13.0


def test_investment_bank_empty() -> None:
    """Тест инвесткопилки на пустых данных."""
    assert investment_bank("2020-05", [], 50) == 0.0


def test_get_profitable_cashback_categories(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тест расчета выгодных категорий кэшбэка."""
    # -1712 // 100 * 1 = 17
    # -50 // 100 * 1 = 0
    # -105 // 100 * 1 = 1
    # Супермаркеты: 17 + 1 = 18. Фастфуд: 0. Пополнения (плюс) — мимо.
    json_result = get_profitable_cashback_categories(sample_transactions, 2020, 5)
    result = json.loads(json_result)

    assert "Супермаркеты" in result
    assert result["Супермаркеты"] == 18
    assert "Фастфуд" not in result  # Так как там 0 рублей кэшбэка
