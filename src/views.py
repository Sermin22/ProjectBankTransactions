import os
import json
from src.utils import greet_by_time, process_xlsx_file_with_date_filter, top_transactions_by_amount, \
    recent_currency_rates, stock_prices_func


def main_page(datetime_str):

    PATH_TO_FILE_XLSX = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "operations.xlsx")

    greeting = greet_by_time(datetime_str)
    cards = process_xlsx_file_with_date_filter(PATH_TO_FILE_XLSX, datetime_str)
    top_transactions = top_transactions_by_amount(PATH_TO_FILE_XLSX, datetime_str)
    currency_rates = recent_currency_rates()
    stock_prices = stock_prices_func()

    # Получаем абсолютный путь к корневой директории проекта
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Указываем путь к записи user_settings.json
    file_json_path = os.path.join(BASE_DIR, "user_settings.json")
    # Данные, которые необходимо записать в файл
    user_currencies = ["USD", "EUR"]
    user_stocks = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]

    # Создаем словарь с данными
    user_settings = {
        "user_currencies": user_currencies,
        "user_stocks": user_stocks
    }
    # Запись данных в файл
    with open(file_json_path, "w") as file:
        json.dump(user_settings, file, indent=4)

    # Объединяем все данные в один словарь
    data = {
        "greeting": greeting,
        "cards": cards,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }
    # Преобразуем словарь в строку JSON
    json_response = json.dumps(data, ensure_ascii=False)
    return json_response


if __name__ == '__main__':
    print(main_page('2021-12-31 16:44:00'))  # YYYY-MM-DD HH:MM:SS

# result = '''
# {"greeting": "Добрый день",
#     "cards": [
#         {"Номер карты": 0, "Сумма платежа": 84830.55, "Кэшбэк": 0.0},
#         {"Номер карты": "*4556", "Сумма платежа": 3775.7000000000003, "Кэшбэк": 181.0},
#         {"Номер карты": "*5091", "Сумма платежа": 15193.330000000002, "Кэшбэк": 0.0},
#         {"Номер карты": "*7197", "Сумма платежа": 24576.629999999997, "Кэшбэк": 0.0}],
#     "top_transactions": [
#         {"Дата операции": "22.12.2021", "Сумма платежа": 28001.94, "Категория": "Переводы",
#           "Описание": "Перевод Кредитная карта. ТП 10.2 RUR"},
#         {"Дата операции": "30.12.2021", "Сумма платежа": 20000.0, "Категория": "Переводы",
#           "Описание": "Константин Л."},
#         {"Дата операции": "16.12.2021", "Сумма платежа": 14216.42, "Категория": "ЖКХ",
#           "Описание": "ЖКУ Квартира"},
#         {"Дата операции": "23.12.2021", "Сумма платежа": 10000.0, "Категория": "Переводы",
#           "Описание": "Светлана Т."},
#         {"Дата операции": "02.12.2021", "Сумма платежа": 5510.8, "Категория": "Каршеринг",
#           "Описание": "Ситидрайв"}],
#     "currency_rates": [
#         {"currency": "USD", "rate": 1.033816},
#         {"currency": "EUR", "rate": 1}],
#     "stock_prices": [
#         {"symbol": "TSLA", "close": 374.32},
#         {"symbol": "AMZN", "close": 238.83},
#         {"symbol": "GOOGL", "close": 191.6},
#         {"symbol": "MSFT", "close": 415.82},
#         {"symbol": "AAPL", "close": 233.22}]
#  }'''
