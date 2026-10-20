import os
from typing import Any, Dict, List

import pandas as pd



def load_operations_from_excel(file_path: str) -> List[Dict[str, Any]]:
    """Читает Excel-файл с транзакциями и возвращает список словарей.

    Если файл не найден или пустой, возвращает пустой список.
    """
    if not os.path.exists(file_path):
        return []

    try:
        # Читаем эксельку через pandas, пустые ячейки заменяем на None для чистоты данных
        df = pd.read_excel(file_path)
        df = df.where(pd.notnull(df), None)

        # Конвертируем DataFrame в список словарей, как того требует стандартная практика
        transactions: List[Dict[str, Any]] = df.to_dict(orient="records")
        return transactions
    except Exception:
        # Если прилетит битый файл, приложение не должно упасть с 500 ошибкой
        return []
