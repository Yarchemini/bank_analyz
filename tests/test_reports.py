from unittest.mock import patch
import pandas as pd
from src.reports import spending_by_category, spending_by_weekday, spending_by_workday, report_to_file


def test_report_to_file_decorator_exception() -> None:
    """Тест декоратора, если запись в Excel вызвала ошибку (проверка блока except)."""

    @report_to_file(filename="invalid_path/report.xlsx")
    def dummy_func() -> pd.DataFrame:
        return pd.DataFrame([{"test": 1}])

    res = dummy_func()
    assert not res.empty


def test_spending_by_category_empty() -> None:
    """Тест отчета по категориям с пустым DataFrame."""
    df = pd.DataFrame()
    res = spending_by_category(df, "Одежда")
    assert res.empty


@patch("src.reports.pd.DataFrame.to_excel")
def test_spending_by_category_success(mock_to_excel: patch) -> None:
    """Тест успешной фильтрации трат по конкретной категории."""
    data = pd.DataFrame([
        {"Дата операции": "10.05.2020 12:00:00", "Категория": "Одежда", "Сумма операции": -2500.0},
        {"Дата операции": "12.05.2020 15:00:00", "Категория": "Фастфуд", "Сумма операции": -500.0},
        {"Дата операции": "01.01.2020 10:00:00", "Категория": "Одежда", "Сумма операции": -3000.0}
    ])

    res = spending_by_category(data, "Одежда", date="2020-05-20 00:00:00")
    assert len(res) == 1
    assert res.iloc[0]["Сумма операции"] == -2500.0


def test_spending_by_weekday_empty() -> None:
    """Тест отчета по дням недели с пустым DataFrame или без подходящих трат."""
    df = pd.DataFrame()
    res = spending_by_weekday(df, date="2020-05-20 00:00:00")
    assert res.empty


@patch("src.reports.pd.DataFrame.to_excel")
def test_spending_by_weekday_success(mock_to_excel: patch) -> None:
    """Тест успешного подсчета средних трат по дням недели."""
    data = pd.DataFrame([
        {"Дата операции": "10.05.2020 12:00:00", "Сумма операции": -2000.0},
        {"Дата операции": "10.05.2020 18:00:00", "Сумма операции": -4000.0}
    ])
    res = spending_by_weekday(data, date="2020-05-20 00:00:00")
    assert not res.empty
    assert res.iloc[0]["Средняя сумма"] == 3000.0


def test_spending_by_workday_empty() -> None:
    """Тест отчета по рабочим/выходным с пустым DataFrame."""
    df = pd.DataFrame()
    res = spending_by_workday(df, date="2020-05-20 00:00:00")
    assert res.empty


@patch("src.reports.pd.DataFrame.to_excel")
def test_spending_by_workday_success(mock_to_excel: patch) -> None:
    """Тест успешного разделения трат на рабочие и выходные дни."""
    data = pd.DataFrame([
        {"Дата операции": "10.05.2020 12:00:00", "Сумма операции": -2000.0},
        {"Дата операции": "12.05.2020 12:00:00", "Сумма операции": -1000.0}
    ])
    res = spending_by_workday(data, date="2020-05-20 00:00:00")
    assert len(res) == 2
