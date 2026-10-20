import json
import re
from typing import Any, Dict, List


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """Рассчитывает сумму, отложенную в Инвесткопилку за указанный месяц за счет округления трат."""
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
    """Анализирует транзакции за определенный год и месяц и возвращает JSON-строку с расчетом кешбэка."""
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
                if category in category_cashback:
                    category_cashback[category] += cashback
                else:
                    category_cashback[category] = cashback

    final_analysis = {k: int(v) for k, v in category_cashback.items()}
    return json.dumps(final_analysis, ensure_ascii=False, indent=4)


def simple_search(query: str, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Осуществляет поиск транзакций по подстроке в категориях и описании без учета регистра."""
    if not query:
        return []

    search_query = query.lower().strip()
    result = []

    for tx in transactions:
        category = str(tx.get("Категория") or tx.get("category", "")).lower()
        description = str(tx.get("Описание") or tx.get("description", "")).lower()

        if search_query in category or search_query in description:
            result.append(tx)

    return result


def search_by_phone(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Находит транзакции, содержащие телефонные номера в различных форматах."""
    # Регулярка ловит: +79000000000, 89000000000, +7 (900) 000-00-00, +7 900 000 00 00 и т.д.
    phone_pattern = re.compile(r'(?:\+7|8)\s*\(?\d{3}\)?\s*\d{3}[-\s]*\d{2}[-\s]*\d{2}|\b\d{11}\b')
    result = []

    for tx in transactions:
        description = str(tx.get("Описание") or tx.get("description", ""))
        if phone_pattern.search(description):
            result.append(tx)

    return result

def search_transfers_to_individuals(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Находит транзакции по переводам физлицам.

    Категория должна быть строго 'Переводы', а в описании — Имя и первая буква Фамилии с точкой.
    """
    result = []
    # Регулярка ищет паттерны типа 'Валерий А.', 'Сергей З.', 'Артем П.'
    # Учитываем, что перед именем может быть любой текст (например, 'Константин Л.')
    name_pattern = re.compile(r'\b[А-ЯA-Z][а-яa-z]+\s+[А-ЯA-Z]\.')

    for tx in transactions:
        category = str(tx.get("Категория") or tx.get("category", "")).strip()
        description = str(tx.get("Описание") or tx.get("description", "")).strip()

        if category.lower() == "переводы":
            if name_pattern.search(description):
                result.append(tx)

    return result
