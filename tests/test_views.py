import pytest
import json
from unittest.mock import patch
from src.views import main_page


@pytest.fixture
def mocked_responses():
    """Фикстура для подготовки моков"""

    with patch('src.views.greet_by_time') as mock_greet_by_time, \
         patch('src.views.process_xlsx_file_with_date_filter') as mock_process_xlsx, \
         patch('src.views.top_transactions_by_amount') as mock_top_transactions, \
         patch('src.views.recent_currency_rates') as mock_currency_rates, \
         patch('src.views.stock_prices_func') as mock_stock_prices:

        yield mock_greet_by_time, mock_process_xlsx, mock_top_transactions, mock_currency_rates, mock_stock_prices


def test_main_page(mocked_responses):
    '''Тестирование главной функции, принимающей на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS
        и возвращающей JSON-ответ со следующими данными: приветствие в зависимости от времени суток, по каждой карте:
        последние 4 цифры карты, общую сумма расходов, кешбэк, топ-5 транзакций по сумме платежа, курс валют и
        стоимость акций из S&P500'''

    # Разворачиваем фикстуру
    (mock_greet_by_time, mock_process_xlsx, mock_top_transactions, mock_currency_rates,
     mock_stock_prices) = mocked_responses

    # Настраиваем мокированные значения для вспомогательных функций
    mock_greet_by_time.return_value = 'Доброе утро!'
    mock_process_xlsx.return_value = [
        {'card': '1234', 'total_expenses': 1000, 'cashback': 50},
        {'card': '5678', 'total_expenses': 2000, 'cashback': 100}
    ]
    mock_top_transactions.return_value = [
        {'amount': 500, 'description': 'Покупка'},
        {'amount': 400, 'description': 'Оплата услуг'}
    ]
    mock_currency_rates.return_value = {'USD': 75, 'EUR': 85}
    mock_stock_prices.return_value = {'AAPL': 150, 'AMZN': 3000}

    # Вызываем главную функцию
    result = main_page("2023-10-01 08:00:00")

    # Проверяем результат
    expected_result = {
        "greeting": "Доброе утро!",
        "cards": [
            {"card": "1234", "total_expenses": 1000, "cashback": 50},
            {"card": "5678", "total_expenses": 2000, "cashback": 100}
        ],
        "top_transactions": [
            {"amount": 500, "description": "Покупка"},
            {"amount": 400, "description": "Оплата услуг"}
        ],
        "currency_rates": {"USD": 75, "EUR": 85},
        "stock_prices": {"AAPL": 150, "AMZN": 3000}
    }

    assert json.loads(result) == expected_result
