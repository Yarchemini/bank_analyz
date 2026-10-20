import json
import os
import pandas as pd

from src.reports import spending_by_weekday, spending_by_workday
from src.services import search_by_phone, search_transfers_to_individuals, simple_search
from src.utils import load_operations_from_excel
from src.views import generate_events_page_data, generate_main_page_data


def main() -> None:
    """Основная функция приложения."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    excel_path = os.path.join(base_dir, "data", "operations.xlsx")
    settings_path = os.path.join(base_dir, "user_settings.json")

    print("=== ЗАПУСК БАНКОВСКОГО АНАЛИЗАТОРА ===")

    transactions = load_operations_from_excel(excel_path)
    print(f"[Успех] Загружено транзакций из Excel: {len(transactions)}")

    try:
        transactions_df = pd.read_excel(excel_path)
    except Exception:
        transactions_df = pd.DataFrame()

    test_date_str = "2021-12-31 18:00:00"

    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        settings = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN"]}

    currencies = settings.get("user_currencies", [])
    stocks = settings.get("user_stocks", [])

    print("\n--- [Генерация] Главная страница ---")
    print(generate_main_page_data(test_date_str, transactions, currencies, stocks)[:500] + "\n...")

    print("\n--- [Генерация] Страница 'События' ---")
    print(generate_events_page_data(test_date_str, transactions, currencies, stocks, range_type="M")[:500] + "\n...")

    print("\n--- [Сервис] Простой поиск ---")
    search_json = simple_search("Супермаркеты", transactions)
    print(f"JSON валиден, объектов внутри: {len(json.loads(search_json))}")

    print("\n--- [Сервис] Поиск по телефонам ---")
    phone_json = search_by_phone(transactions)
    print(f"JSON валиден, объектов внутри: {len(json.loads(phone_json))}")

    print("\n--- [Сервис] Поиск переводов физлицам ---")
    ind_json = search_transfers_to_individuals(transactions)
    print(f"JSON валиден, объектов внутри: {len(json.loads(ind_json))}")

    print("\n--- [Генерация] Формирование Excel-отчётов ---")
    spending_by_weekday(transactions_df, test_date_str)
    spending_by_workday(transactions_df, test_date_str)
    print("[Успех] Все файлы сгенерированы в data/ по госту!")


if __name__ == "__main__":
    main()
