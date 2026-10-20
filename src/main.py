from datetime import datetime
import json
import os

from src.services import get_profitable_cashback_categories, investment_bank
from src.utils import load_operations_from_excel
from src.views import generate_main_page_data


def main() -> None:
    """Основная функция приложения.

    Связывает чтение данных, генерацию главной страницы и аналитические сервисы.
    """
    # Определяем базовые пути (работает и у тебя в prj, и у Матвея в Pythin)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    excel_path = os.path.join(base_dir, "data", "operations.xlsx")
    settings_path = os.path.join(base_dir, "user_settings.json")

    print("=== Запуск анализатора транзакций ===")

    # 1. Вызываем изолированное чтение данных из utils
    transactions = load_operations_from_excel(excel_path)
    print(f"Загружено транзакций из Excel: {len(transactions)}")

    # Задаем тестовую дату для генерации (например, май 2020 года, как в ТЗ)
    test_date_str = "2020-05-20 14:00:00"

    # 2. Логика веб-страницы 'Главная' из views
    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            settings = json.load(f)
    except Exception:
        settings = {"user_currencies": ["USD", "EUR"], "user_stocks": ["AAPL", "AMZN"]}

    currencies = settings.get("user_currencies", [])
    stocks = settings.get("user_stocks", [])

    print("\n--- Генерация данных для Главной страницы ---")
    main_page_json = generate_main_page_data(test_date_str, transactions, currencies, stocks)
    print(main_page_json)

    # 3. Работа сервисов из services
    print("\n--- Тестирование сервиса 'Инвесткопилка' ---")
    saved_money = investment_bank("2020-05", transactions, limit=50)
    print(f"За май 2020 при округлении до 50 руб. удалось бы скопить: {saved_money} руб.")

    print("\n--- Тестирование сервиса 'Выгодный кэшбэк' ---")
    cashback_json = get_profitable_cashback_categories(transactions, 2020, 5)
    print(cashback_json)


if __name__ == "__main__":
    main()
