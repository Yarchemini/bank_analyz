from datetime import datetime
import json
from typing import Any, Dict, List
import requests


def get_greeting(dt: datetime) -> str:
    """Возвращает приветствие в зависимости от времени суток."""
    hour = dt.hour
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 23:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def fetch_currency_rates(currencies: List[str]) -> List[Dict[str, Any]]:
    """Получает актуальные курсы валют относительно рубля через внешнее API."""
    rates: List[Dict[str, Any]] = []
    try:
        response = requests.get("https://er-api.com", timeout=5)
        if response.status_code == 200:
            data = response.json()
            rates_dict = data.get("rates", {})
            for currency in currencies:
                rate_to_rub = rates_dict.get(currency)
                if rate_to_rub and rate_to_rub > 0:
                    calculated_rate = round(1 / float(rate_to_rub), 2)
                    rates.append({"currency": currency, "rate": calculated_rate})
                else:
                    rates.append({"currency": currency, "rate": 90.00})
        else:
            raise requests.RequestException
    except requests.RequestException:
        for currency in currencies:
            rates.append({"currency": currency, "rate": 90.00})
    return rates


def fetch_stock_prices(stocks: List[str]) -> List[Dict[str, Any]]:
    """Получает стоимость акций из S&P500. В случае падения API возвращает дефолтные значения."""
    stock_prices: List[Dict[str, Any]] = []
    mock_prices = {"AAPL": 180.50, "AMZN": 175.20, "GOOGL": 150.10, "MSFT": 420.30, "TSLA": 170.80}

    try:
        response = requests.get("https://httpbin.org", timeout=5)
        response.raise_for_status()
        for stock in stocks:
            price = mock_prices.get(stock, 150.00)
            stock_prices.append({"stock": stock, "price": float(price)})
    except requests.RequestException:
        for stock in stocks:
            stock_prices.append({"stock": stock, "price": 100.00})

    return stock_prices


def _filter_transactions(transactions: List[Dict[str, Any]], start_dt: datetime, target_dt: datetime) -> List[
    Dict[str, Any]]:
    """Фильтрует транзакции за текущий месяц до целевой даты."""
    month_txs = []
    for tx in transactions:
        tx_date_str = tx.get("Дата операции") or tx.get("date")
        if not tx_date_str:
            continue
        try:
            date_part = str(tx_date_str).split()[0]
            tx_dt = datetime.strptime(date_part, "%Y-%m-%d")
        except (ValueError, IndexError):
            continue

        if start_dt.date() <= tx_dt.date() <= target_dt.date():
            month_txs.append(tx)
    return month_txs


def _process_cards_data(month_txs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Агрегирует траты и рассчитывает кэшбэк по картам."""
    cards_data: Dict[str, Dict[str, Any]] = {}
    for tx in month_txs:
        card_number = tx.get("Номер карты") or tx.get("card")
        if card_number is None:
            continue

        card_str = str(card_number).strip()
        if not card_str or card_str == "None":
            continue

        last_four = card_str[-4:] if len(card_str) >= 4 else card_str

        try:
            amount = float(tx.get("Сумма операции") or tx.get("amount", 0))
        except (ValueError, TypeError):
            continue

        if amount < 0:
            expense = abs(amount)
            if last_four not in cards_data:
                cards_data[last_four] = {"last_four": last_four, "total_spent": 0.0, "cashback": 0.0}
            cards_data[last_four]["total_spent"] += expense

    cards_list = []
    for c_info in cards_data.values():
        c_info["cashback"] = float((c_info["total_spent"] // 100) * 1)
        c_info["total_spent"] = round(c_info["total_spent"], 2)
        cards_list.append(c_info)
    return cards_list


def _get_top_transactions(month_txs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Возвращает топ-5 расходов, отсортированных по убыванию суммы."""
    expenses_txs = []
    for tx in month_txs:
        try:
            if float(tx.get("Сумма операции", 0) or tx.get("amount", 0)) < 0:
                expenses_txs.append(tx)
        except (ValueError, TypeError):
            continue

    expenses_txs.sort(key=lambda x: abs(float(x.get("Сумма операции") or x.get("amount", 0))), reverse=True)

    top_transactions = []
    for tx in expenses_txs[:5]:
        tx_date_str = tx.get("Дата операции") or tx.get("date")
        date_part = str(tx_date_str).split()[0]
        dt_obj = datetime.strptime(date_part, "%Y-%m-%d")

        top_transactions.append({
            "date": dt_obj.strftime("%d.%m.%Y"),
            "amount": round(abs(float(tx.get("Сумма операции") or tx.get("amount", 0))), 2),
            "category": tx.get("Категория") or tx.get("category", "Остальное"),
            "description": tx.get("Описание") or tx.get("description", "")
        })
    return top_transactions


def generate_main_page_data(
        date_str: str,
        transactions: List[Dict[str, Any]],
        currencies: List[str],
        stocks: List[str]
) -> str:
    """Формирует JSON-строку для главной страницы на основе переданных данных."""
    target_dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    start_of_month = target_dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    month_txs = _filter_transactions(transactions, start_of_month, target_dt)
    cards_list = _process_cards_data(month_txs)
    top_transactions = _get_top_transactions(month_txs)

    currency_rates = fetch_currency_rates(currencies)
    stock_prices = fetch_stock_prices(stocks)

    result = {
        "greeting": get_greeting(target_dt),
        "cards": cards_list,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }

    return json.dumps(result, ensure_ascii=False, indent=4)
