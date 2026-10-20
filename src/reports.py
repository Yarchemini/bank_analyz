from functools import wraps
from typing import Any, Callable

import pandas as pd


def report_to_file(filename: str = "report.xlsx") -> Callable[..., Callable[..., Any]]:
    """Декоратор, который автоматически записывает возвращаемый Pandas DataFrame в Excel-файл."""

    def decorator(func: Callable[..., pd.DataFrame]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> pd.DataFrame:
            df = func(*args, **kwargs)
            try:
                df.to_excel(filename, index=False)
            except Exception:
                pass

            return df

        return wrapper

    return decorator


@report_to_file(filename="data/spending_by_category.xlsx")
def get_spending_by_category(transactions_df: pd.DataFrame, category: str, date_str: str = "") -> pd.DataFrame:
    """Фильтрует траты по заданной категории за последние 3 месяца от указанной даты."""
    if transactions_df.empty:
        return pd.DataFrame()

    if date_str:
        target_date = pd.to_datetime(date_str, format="%Y-%m-%d %H:%M:%S")
    else:
        target_date = pd.Timestamp.now()

    start_date = target_date - pd.DateOffset(months=3)

    date_col = "Дата операции" if "Дата операции" in transactions_df.columns else "date"
    transactions_df[date_col] = pd.to_datetime(transactions_df[date_col], dayfirst=True)

    cat_col = "Категория" if "Категория" in transactions_df.columns else "category"
    amount_col = "Сумма операции" if "Сумма операции" in transactions_df.columns else "amount"

    filtered_df = transactions_df[
        (transactions_df[cat_col].str.lower() == category.lower()) &
        (transactions_df[date_col] >= start_date) &
        (transactions_df[date_col] <= target_date) &
        (transactions_df[amount_col].astype(float) < 0)
        ]

    return filtered_df


@report_to_file(filename="data/spending_by_weekday.xlsx")
def get_spending_by_weekday(transactions_df: pd.DataFrame, date_str: str = "") -> pd.DataFrame:
    """Вычисляет средние траты в каждый из дней недели за последние 3 месяца от указанной даты."""
    if transactions_df.empty:
        return pd.DataFrame()

    if date_str:
        target_date = pd.to_datetime(date_str, format="%Y-%m-%d %H:%M:%S")
    else:
        target_date = pd.Timestamp.now()

    start_date = target_date - pd.DateOffset(months=3)

    date_col = "Дата операции" if "Дата операции" in transactions_df.columns else "date"
    transactions_df[date_col] = pd.to_datetime(transactions_df[date_col], dayfirst=True)

    amount_col = "Сумма операции" if "Сумма операции" in transactions_df.columns else "amount"

    # Фильтруем за 3 месяца и только расходы (сумма < 0)
    filtered_df = transactions_df[
        (transactions_df[date_col] >= start_date) &
        (transactions_df[date_col] <= target_date) &
        (transactions_df[amount_col].astype(float) < 0)
        ].copy()

    if filtered_df.empty:
        return pd.DataFrame(columns=["День недели", "Средняя сумма"])

    # Извлекаем название дня недели на английском (или числом) и берем модуль суммы расходов
    filtered_df["Day_of_Week"] = filtered_df[date_col].dt.day_name()
    filtered_df["Expense_Amount"] = filtered_df[amount_col].astype(float).abs()

    # Группируем по дням недели и считаем среднее значение трат
    summary = filtered_df.groupby("Day_of_Week")["Expense_Amount"].mean().reset_index()
    summary.columns = ["День недели", "Средняя сумма"]
    summary["Средняя сумма"] = summary["Средняя сумма"].round(2)

    return summary


@report_to_file(filename="data/spending_workday_weekend.xlsx")
def get_spending_workday_weekend(transactions_df: pd.DataFrame, date_str: str = "") -> pd.DataFrame:
    """Выводит средние траты в рабочие и выходные дни за последние 3 месяца от указанной даты."""
    if transactions_df.empty:
        return pd.DataFrame()

    if date_str:
        target_date = pd.to_datetime(date_str, format="%Y-%m-%d %H:%M:%S")
    else:
        target_date = pd.Timestamp.now()

    start_date = target_date - pd.DateOffset(months=3)

    date_col = "Дата операции" if "Дата операции" in transactions_df.columns else "date"
    transactions_df[date_col] = pd.to_datetime(transactions_df[date_col], dayfirst=True)

    amount_col = "Сумма операции" if "Сумма операции" in transactions_df.columns else "amount"

    filtered_df = transactions_df[
        (transactions_df[date_col] >= start_date) &
        (transactions_df[date_col] <= target_date) &
        (transactions_df[amount_col].astype(float) < 0)
        ].copy()

    if filtered_df.empty:
        return pd.DataFrame(columns=["Тип дня", "Средняя сумма"])

    # .dt.dayofweek возвращает 5 для субботы и 6 для воскресенья
    filtered_df["Is_Weekend"] = filtered_df[date_col].dt.dayofweek.isin([5, 6])
    filtered_df["Day_Type"] = filtered_df["Is_Weekend"].map({True: "Выходной день", False: "Рабочий день"})
    filtered_df["Expense_Amount"] = filtered_df[amount_col].astype(float).abs()

    # Агрегируем среднее
    summary = filtered_df.groupby("Day_Type")["Expense_Amount"].mean().reset_index()
    summary.columns = ["Тип дня", "Средняя сумма"]
    summary["Средняя сумма"] = summary["Средняя сумма"].round(2)

    return summary
