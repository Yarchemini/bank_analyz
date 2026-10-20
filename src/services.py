import json
import re
from typing import Any, Dict, List


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """Рассчитывает сумму, отложенную в Инвесткопилку."""
    total_saved = 0.0
    for tx in transactions:
        date_op = tx.get("Дата операции") or tx.get("date")
        if not date_op or not str(date_op).startswith(month):
            continue
        amount_op = tx.get("Сумма операции") or tx.get("amount")
        if amount_op is None:
            continue
        try:
            amount = float(amount_op)
        except (ValueError, TypeError):
            continue
        if amount < 0:
            raw_expense = abs(amount)
            if raw_expense % limit == 0:
                continue
            rounded_expense = ((raw_expense // limit) + 1) * limit
            total_saved += rounded_expense - raw_expense
    return round(total_saved, 2)


def get_profitable_cashback_categories(data: List[Dict[str, Any]], year: int, month: int) -> str:
    """Анализирует выгодность категорий повышенного кешбэка."""
    category_cashback: Dict[str, float] = {}
    month_str = f"{year}-{month:02d}"
    for tx in data:
        date_op = tx.get("Дата операции") or tx.get("date")
        if not date_op or not str(date_op).startswith(month_str):
            continue
        category = tx.get("Категория") or tx.get("category")
        amount_op = tx.get("Сумма операции") or tx.get("amount")
        if not category or amount_op is None:
            continue
        try:
            amount = float(amount_op)
        except (ValueError, TypeError):
            continue
        if amount < 0:
            raw_expense = abs(amount)
            cashback = float((raw_expense // 100) * 1)
            if cashback > 0:
                category_cashback[category] = category_cashback.get(category, 0.0) + cashback
    return json.dumps({k: int(v) for k, v in category_cashback.items()}, ensure_ascii=False, indent=4)


def simple_search(query: str, transactions: List[Dict[str, Any]]) -> str:
    """Осуществляет поиск транзакций по подстроке и возвращает JSON-строку."""
    if not query:
        return json.dumps([], ensure_ascii=False)
    search_query = query.lower().strip()
    result = []
    for tx in transactions:
        category = str(tx.get("Категория") or tx.get("category", "")).lower()
        description = str(tx.get("Описание") or tx.get("description", "")).lower()
        if search_query in category or search_query in description:
            result.append(tx)
    return json.dumps(result, ensure_ascii=False, indent=4)


def search_by_phone(transactions: List[Dict[str, Any]]) -> str:
    """Находит транзакции с телефонными номерами и возвращает JSON-строку."""
    phone_pattern = re.compile(r'(?:\+7|8)\s*\(?\d{3}\)?\s*\d{3}[-\s]*\d{2}[-\s]*\d{2}|\b\d{11}\b')
    result = []
    for tx in transactions:
        description = str(tx.get("Описание") or tx.get("description", ""))
        if phone_pattern.search(description):
            result.append(tx)
    return json.dumps(result, ensure_ascii=False, indent=4)


def search_transfers_to_individuals(transactions: List[Dict[str, Any]]) -> str:
    """Находит транзакции по переводам физлицам и возвращает JSON-строку."""
    result = []
    name_pattern = re.compile(r'\b[А-ЯA-Z][а-яa-z]+\s+[А-ЯA-Z]\.')
    for tx in transactions:
        category = str(tx.get("Категория") or tx.get("category", "")).strip()
        description = str(tx.get("Описание") or tx.get("description", ""))
        if category.lower() == "переводы" and name_pattern.search(description):
            result.append(tx)
    return json.dumps(result, ensure_ascii=False, indent=4)