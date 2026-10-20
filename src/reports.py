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
    transactions_df[date_col] = pd.to_datetime(transactions_df[date_col])

    cat_col = "Категория" if "Категория" in transactions_df.columns else "category"
    amount_col = "Сумма операции" if "Сумма операции" in transactions_df.columns else "amount"

    filtered_df = transactions_df[
        (transactions_df[cat_col].str.lower() == category.lower()) &
        (transactions_df[date_col] >= start_date) &
        (transactions_df[date_col] <= target_date) &
        (transactions_df[amount_col].astype(float) < 0)
    ]

    return filtered_df
