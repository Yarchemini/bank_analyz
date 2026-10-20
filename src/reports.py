from functools import wraps
from typing import Any, Callable, Optional
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
def spending_by_category(
    transactions: pd.DataFrame,
    category: str,
    date: Optional[str] = None
) -> pd.DataFrame:
    """Фильтрует траты по заданной категории за последние 3 месяца от указанной даты."""
    if transactions.empty:
        return pd.DataFrame()

    target_date = pd.to_datetime(date, format="%Y-%m-%d %H:%M:%S") if date else pd.Timestamp.now()
    start_date = target_date - pd.DateOffset(months=3)

    date_col = "Дата операции" if "Дата операции" in transactions.columns else "date"
    transactions[date_col] = pd.to_datetime(transactions[date_col], dayfirst=True)

    cat_col = "Категория" if "Категория" in transactions.columns else "category"
    amount_col = "Сумма операции" if "Сумма операции" in transactions.columns else "amount"

    return transactions[
        (transactions[cat_col].str.lower() == category.lower()) &
        (transactions[date_col] >= start_date) &
        (transactions[date_col] <= target_date) &
        (transactions[amount_col].astype(float) < 0)
    ]


@report_to_file(filename="data/spending_by_weekday.xlsx")
def spending_by_weekday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Вычисляет средние траты в каждый из дней недели за последние 3 месяца от указанной даты."""
    if transactions.empty:
        return pd.DataFrame()

    target_date = pd.to_datetime(date, format="%Y-%m-%d %H:%M:%S") if date else pd.Timestamp.now()
    start_date = target_date - pd.DateOffset(months=3)

    date_col = "Дата операции" if "Дата операции" in transactions.columns else "date"
    transactions[date_col] = pd.to_datetime(transactions[date_col], dayfirst=True)
    amount_col = "Сумма операции" if "Сумма операции" in transactions.columns else "amount"

    filtered_df = transactions[
        (transactions[date_col] >= start_date) &
        (transactions[date_col] <= target_date) &
        (transactions[amount_col].astype(float) < 0)
    ].copy()

    if filtered_df.empty:
        return pd.DataFrame(columns=["День недели", "Средняя сумма"])

    filtered_df["Day_of_Week"] = filtered_df[date_col].dt.day_name()
    filtered_df["Expense_Amount"] = filtered_df[amount_col].astype(float).abs()

    summary = filtered_df.groupby("Day_of_Week")["Expense_Amount"].mean().reset_index()
    summary.columns = ["День недели", "Средняя сумма"]
    summary["Средняя сумма"] = summary["Средняя сумма"].round(2)
    return summary


@report_to_file(filename="data/spending_workday_weekend.xlsx")
def spending_by_workday(transactions: pd.DataFrame, date: Optional[str] = None) -> pd.DataFrame:
    """Выводит средние трат в рабочие и выходные дни за последние 3 месяца от указанной даты."""
    if transactions.empty:
        return pd.DataFrame()

    target_date = pd.to_datetime(date, format="%Y-%m-%d %H:%M:%S") if date else pd.Timestamp.now()
    start_date = target_date - pd.DateOffset(months=3)

    date_col = "Дата операции" if "Дата операции" in transactions.columns else "date"
    transactions[date_col] = pd.to_datetime(transactions[date_col], dayfirst=True)
    amount_col = "Сумма операции" if "Сумма операции" in transactions.columns else "amount"

    filtered_df = transactions[
        (transactions[date_col] >= start_date) &
        (transactions[date_col] <= target_date) &
        (transactions[amount_col].astype(float) < 0)
    ].copy()

    if filtered_df.empty:
        return pd.DataFrame(columns=["Тип дня", "Средняя сумма"])

    filtered_df["Is_Weekend"] = filtered_df[date_col].dt.dayofweek.isin([5, 6])
    filtered_df["Day_Type"] = filtered_df["Is_Weekend"].map({True: "Выходной день", False: "Рабочий день"})
    filtered_df["Expense_Amount"] = filtered_df[amount_col].astype(float).abs()

    summary = filtered_df.groupby("Day_Type")["Expense_Amount"].mean().reset_index()
    summary.columns = ["Тип дня", "Средняя сумма"]
    summary["Средняя сумма"] = summary["Средняя сумма"].round(2)
    return summary
