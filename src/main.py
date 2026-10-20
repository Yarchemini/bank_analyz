import json
import os
import pandas as pd

from src.reports import get_spending_by_weekday, get_spending_workday_weekend
from src.services import search_by_phone, search_transfers_to_individuals, simple_search
from src.utils import load_operations_from_excel
from src.views import generate_events_page_data, generate_main_page_data


def main() -> None:
    """Основная функция приложения.

    Связывает чтение данных, генерацию страниц, отчётов и аналитические сервисы.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    excel_path = os.path.join(base_dir, "data", "operations.xlsx")
    settings_path = os.path.join(base_dir, "user_settings.json")

    print("=== ЗАПУСК БАНКОВСКОГО АНАЛИЗАТОРА ===")

    # 1. Загрузка данных
    transactions = load_operations_from_excel(excel_path)
    print(f"[Успех] Загружено транзакций из Excel: {len(transactions)}")

    # Загружаем DataFrame для работы Pandas-отчётов
    try:
        transactions_df = pd.read_excel(excel_path)
    except Exception:
        transactions_df = pd.DataFrame()

    # Задаем базовую дату для тестов (например, декабрь 2021)
    test_date_str = "2021-12-31 18:00:00"

    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        settings = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN"]}

    currencies = settings.get("user_currencies", [])
    stocks = settings.get("user_stocks", [])

    # 2. Тест Главной страницы
    print("\n--- [Генерация] Главная страница ---")
    main_page_json = generate_main_page_data(test_date_str, transactions, currencies, stocks)
    print(main_page_json[:500] + "\n... (вывод обрезан) ...")

    # 3. Тест страницы События
    print("\n--- [Генерация] Страница 'События' (Диапазон: Месяц) ---")
    events_page_json = generate_events_page_data(test_date_str, transactions, currencies, stocks, range_type="M")
    print(events_page_json[:500] + "\n... (вывод обрезан) ...")

    # 4. Тест сервисов поиска
    print("\n--- [Сервис] Простой поиск по запросу 'Супермаркеты' ---")
    search_res = simple_search("Супермаркеты", transactions)
    print(f"Найдено транзакций: {len(search_res)}")

    print("\n--- [Сервис] Поиск транзакций с телефонными номерами ---")
    phone_res = search_by_phone(transactions)
    print(f"Найдено транзакций с телефонами в описании: {len(phone_res)}")

    print("\n--- [Сервис] Поиск переводов физлицам ---")
    individuals_res = search_transfers_to_individuals(transactions)
    print(f"Найдено переводов физлицам по шаблону 'Имя Ф.': {len(individuals_res)}")

    # 5. Тест генерации Excel-отчётов
    print("\n--- [Генерация] Формирование Excel-отчётов за 3 месяца ---")
    get_spending_by_weekday(transactions_df, test_date_str)
    get_spending_workday_weekend(transactions_df, test_date_str)
    print("[Успех] Файлы spending_by_weekday.xlsx и spending_workday_weekend.xlsx созданы в data/")


if __name__ == "__main__":
    main()
