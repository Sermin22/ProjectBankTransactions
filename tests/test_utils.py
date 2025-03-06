import pytest
import pandas as pd
from unittest.mock import patch, Mock
from src.utils import (greet_by_time, process_xlsx_file_with_date_filter, top_transactions_by_amount,
                       stock_prices_func, recent_currency_rates)


@pytest.mark.parametrize('input_date, expected', [
    ('2023-10-01 07:15:00', 'Доброе утро'),
    ('2023-10-01 13:30:00', 'Добрый день'),
    ('2023-10-01 19:45:00', 'Добрый вечер'),
    ('2023-10-01 02:20:00', 'Доброй ночи'),
    ('2023-10', '')
])
def test_greet_by_time(input_date, expected):
    '''Функция тестирует корректность приема на вход строки с датой и временем в формате YYYY-MM-DD HH:MM:SS
    и в зависимости от времени дня вывода приветствия'''
    result = greet_by_time(input_date)
    assert result == expected


@pytest.fixture
def mock_data():
    """Фикстура для создания тестового DataFrame."""
    data = {
        "Дата операции": ["2021-12-30 16:44:00", "2021-12-11 19:03:48", "2021-12-03 22:24:47", "2021-11-26 14:43:37"],
        "Номер карты": ["*7197", "*7197", "*5091", "*7197"],
        "Сумма платежа": [-160.89, -309.0, -496.51, -105.84],
        "Кэшбэк": [float('nan'), 3.09, 4.97, 2]
    }
    df = pd.DataFrame(data)
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], format='%Y-%m-%d %H:%M:%S')
    return df


@patch('pandas.read_excel')
def test_process_xlsx_file_with_date_filter(mock_read_excel, mock_data):
    '''Нормальный исход теста функции, принимающей на вход путь к файлу xlsx, преобразующей в DataFrame и
    далее отфильтровывает по дате операций - конечная дата это дата принимается функцией в качестве
    аргумента в виде строки, а начальная дата - это первый день месяца конечной даты. Группирует по номеру
    карты и агрегирует суммы платежей и кэшбека c получением абсолютного значения суммы платежей.
    Возвращает список словарей при том, что если фильтр по дате находит подходящие записи.'''

    # Устанавливаем возвращаемое значение для read_excel
    mock_read_excel.return_value = mock_data
    input_date = "2021-12-31 16:44:00"
    # Вызываем функцию, которую мы хотим протестировать
    result = process_xlsx_file_with_date_filter("path_to_file.xlsx", input_date)
    expected = [
        {"Номер карты": "*5091", "Сумма платежа": 496.51, "Кэшбэк": 4.97},
        {"Номер карты": "*7197", "Сумма платежа": 469.89, "Кэшбэк": 3.09},
    ]
    assert result == expected


@patch('pandas.read_excel')
def test_process_xlsx_file_with_date_filter_no_date(mock_read_excel, mock_data):
    '''Исход теста функции при том, что если фильтр по дате находит подходящие записи и
    возвращает пустой словарь'''

    # Устанавливаем возвращаемое значение для read_excel
    mock_read_excel.return_value = mock_data
    input_date = "2022-01-10 16:44:00"
    # Вызываем функцию, которую мы хотим протестировать
    result = process_xlsx_file_with_date_filter("path_to_file.xlsx", input_date)
    expected = []
    assert result == expected


@patch('pandas.read_excel')
def test_process_xlsx_file_with_date_filter_no_payments(mock_read_excel, mock_data):
    """Тест случая, когда отсутствуют платежи, то есть все записи имеют положительные значения Суммы платежа."""

    # Меняем значения Суммы платежа на положительные
    mock_data["Сумма платежа"] = [160.89, 309.0, 496.51, 105.84]
    # Устанавливаем возвращаемое значение для read_excel
    mock_read_excel.return_value = mock_data
    # Тестируемый случай: конец месяца
    input_date = "2021-12-31 23:59:59"
    # Вызываем функцию, которую мы хотим протестировать
    result = process_xlsx_file_with_date_filter("path_to_file.xlsx", input_date)
    # Ожидаемый результат: пустой список
    expected = []
    # Сравниваем результаты
    assert result == expected


@pytest.fixture
def mock_data_2():
    """Фикстура для создания тестового DataFrame."""

    # Создаем словарь с данными
    data = {
        "Дата операции":
            ["2021-12-30 16:44:00", "2021-12-25 19:03:48", "2021-12-15 22:24:47", "2021-12-10 14:43:37",
             "2021-12-05 18:20:33", "2021-09-28 13:45:01", "2021-08-17 21:05:29", "2021-07-02 06:32:58"],
        "Сумма платежа":
            [-160.89, -309.0, -496.51, -105.84, -200.50, -300.75, -400.25, -500.99],
        "Категория":
            ["test_1", "test_1", "test_1", "test_1", "test_1", "test_1", "test_1", "test_1"],
        "Описание":
            ["test_2", "test_2", "test_2", "test_2", "test_2", "test_2", "test_2", "test_2"]
    }
    df = pd.DataFrame(data)
    df['Дата операции'] = pd.to_datetime(df['Дата операции'], format='%Y-%m-%d %H:%M:%S')
    return df


@patch('pandas.read_excel')
def test_top_transactions_by_amount(mock_read_excel, mock_data_2):
    '''Тест функции, принимающей на вход путь к файлу xlsx, преобразующей в DataFrame,
    и фильтрующей по дате операций - конечная дата это дата принимается функцией в качестве
    аргумента в виде строки, а начальная дата - это первый день месяца
    конечной даты. Возвращает список со словарями топ-5 транзакций по сумме платежа.
    Тестируется, если по дате значения найдены, отфильтрованы и возвращены'''

    # Устанавливаем возвращаемое значение для read_excel
    mock_read_excel.return_value = mock_data_2
    input_date = "2021-12-31 16:44:00"
    # Вызываем функцию, которую мы хотим протестировать
    result = top_transactions_by_amount("path_to_file.xlsx", input_date)
    expected = [
        {'Дата операции': '15.12.2021', 'Сумма платежа': 496.51, "Категория": "test_1", "Описание": "test_2"},
        {'Дата операции': '25.12.2021', 'Сумма платежа': 309.0, "Категория": "test_1", "Описание": "test_2"},
        {'Дата операции': '05.12.2021', 'Сумма платежа': 200.5, "Категория": "test_1", "Описание": "test_2"},
        {'Дата операции': '30.12.2021', 'Сумма платежа': 160.89, "Категория": "test_1", "Описание": "test_2"},
        {'Дата операции': '10.12.2021', 'Сумма платежа': 105.84, "Категория": "test_1", "Описание": "test_2"}]
    assert result == expected


@patch('pandas.read_excel')
def test_top_transactions_by_amount_empty_result(mock_read_excel, mock_data_2):
    '''Тест случая, когда фильтр по дате не находит подходящих записей.'''

    # Устанавливаем возвращаемое значение для read_excel
    mock_read_excel.return_value = mock_data_2
    input_date = "2022-12-31 16:44:00"
    # Вызываем функцию, которую мы хотим протестировать
    result = top_transactions_by_amount("path_to_file.xlsx", input_date)
    expected = []
    assert result == expected


def response_json():
    return {
        "pagination": {
            "limit": 100,
            "offset": 0,
            "count": 100,
            "total": 9944
        },
        "data": [
            {
                "open": 374.31,
                "close": 374.32,
                "name": "Tesla Inc",
                "price_currency": "USD",
                "symbol": "TSLA",
                "date": "2024-09-27T00:00:00+0000"
            },
            {
                "open": 237.99,
                "close": 238.83,
                "name": "Amazon.com Inc",
                "price_currency": "USD",
                "symbol": "AMZN",
                "date": "2024-09-27T00:00:00+0000"
            },
            {
                "open": 190.55,
                "close": 191.60,
                "name": "Alphabet Inc Class A",
                "price_currency": "USD",
                "symbol": "GOOGL",
                "date": "2024-09-27T00:00:00+0000"
            },
            {
                "open": 414.71,
                "close": 415.82,
                "name": "Microsoft Corporation",
                "price_currency": "USD",
                "symbol": "MSFT",
                "date": "2024-09-27T00:00:00+0000"
            },
            {
                "open": 232.19,
                "close": 233.22,
                "name": "Apple Inc",
                "price_currency": "USD",
                "symbol": "AAPL",
                "date": "2024-09-27T00:00:00+0000"
            }
        ]
    }


@patch('requests.get')
def test_stock_prices_func(mock_get):
    '''Тест функции, в которой происходит обращение к внешнему API для получения текущей стоимости
    акций из S&P500'''

    # Создаем Mock объект для имитации ответа API
    mock_response = Mock()
    mock_response.json.return_value = response_json()
    mock_response.status_code = 200  # Устанавливаем статус-код успешного ответа
    mock_get.return_value = mock_response

    expected = [{"symbol": "TSLA", "close": 374.32},
                {"symbol": "AMZN", "close": 238.83},
                {"symbol": "GOOGL", "close": 191.6},
                {"symbol": "MSFT", "close": 415.82},
                {"symbol": "AAPL", "close": 233.22}]
    result = stock_prices_func()
    assert result == expected


@patch('requests.get')
def test_stock_prices_func_failed(mock_get):
    '''Тест функции, в которой происходит обращение к внешнему API для получения текущей стоимости
    акций из S&P500 и тест функции, когда запрос к API завершается с ошибкой'''

    # Создаем Mock объект для имитации ответа API
    mock_response = Mock()
    mock_response.json.return_value = response_json()
    mock_response.status_code = 400  # Устанавливаем статус-код ошибки
    mock_get.return_value = mock_response

    with pytest.raises(Exception):
        assert stock_prices_func() == "Запрос не выполнен с кодом состояния: 400"


def currency_rates_response_json():
    return {'success': True, 'timestamp': 1739127963, 'base': 'EUR', 'date': '2025-02-09',
            'rates': {'USD': 1.033218, 'EUR': 1}}


@patch('requests.get')
def test_recent_currency_rates(mock_get):
    '''Тестирвание функции, в которой происходит обращение к внешнему API для получения текущекурса USD и EUR'''

    # Создаем Mock объект для имитации ответа API
    mock_response = Mock()
    mock_response.json.return_value = currency_rates_response_json()
    mock_response.status_code = 200  # Устанавливаем статус-код успешного ответа
    mock_get.return_value = mock_response

    expected = [{"currency": "USD", "rate": 1.033218}, {"currency": "EUR", "rate": 1}]

    result = recent_currency_rates()
    assert result == expected


@patch('requests.get')
def test_recent_currency_rates_failed(mock_get):
    '''Тестирвание функции, в которой происходит обращение к внешнему API для получения текущекурса USD и EUR
    и тест функции, когда запрос к API завершается с ошибкой'''

    # Создаем Mock объект для имитации ответа API
    mock_response = Mock()
    mock_response.json.return_value = currency_rates_response_json()
    mock_response.status_code = 400  # Устанавливаем статус-код успешного ответа
    mock_get.return_value = mock_response

    with pytest.raises(Exception):
        assert recent_currency_rates() == "Запрос не выполнен с кодом состояния: 400"
