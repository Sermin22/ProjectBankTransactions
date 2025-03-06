import pytest
import pandas as pd
from unittest.mock import patch
from src.services import search_string_in_operations


@pytest.fixture
def mock_data():
    """Фикстура для создания тестового DataFrame."""

    # Создаем словарь с данными
    data = {
        "Дата операции":
            ["2021-12-30 16:44:00", "2021-12-25 19:03:48", "2021-12-15 22:24:47", "2021-12-10 14:43:37",
             "2021-12-05 18:20:33", "2021-09-28 13:45:01", "2021-08-17 21:05:29", "2021-07-02 06:32:58"],
        "Сумма платежа":
            [-160.89, -309.0, -496.51, -105.84, -200.50, -300.75, -400.25, -500.99],
        "Категория":
            ["Супермаркеты", "Различные товары", "Каршеринг", "Дом и ремонт", "Транспорт",
             "Развлечения", "Фастфуд", "Связь"],
        "Описание":
            ["Колхоз", "Ozon.ru", "Ситидрайв", "Галамарт", "Bars 2", "sevs.eduerp.ru", "Rumyanyj Khleb", "МТС"]
    }
    df = pd.DataFrame(data)
    return df


@patch('pandas.read_excel')
def test_search_string_in_operations(mock_read_excel, mock_data):
    '''Тестирование функции, принимающей xlsx файл с данными о банковских операциях и строку поиска,
        а возвращает JSON-ответ со всеми транзакциями, содержащими запрос в описании или категории,
        у которых в описании есть данная строка.'''

    # Устанавливаем возвращаемое значение для read_excel
    mock_read_excel.return_value = mock_data
    search = "Супермаркеты"
    expected = ('[{"Дата операции": "2021-12-30 16:44:00", "Сумма платежа": -160.89, '
                '"Категория": "Супермаркеты", "Описание": "Колхоз"}]')

    result = search_string_in_operations("path_to_file.xlsx", search)
    assert result == expected


@patch('pandas.read_excel')
def test_search_string_in_operations_no_data(mock_read_excel, mock_data):
    '''Тестирование функции, принимающей xlsx файл с данными о банковских операциях и строку поиска,
        а возвращает JSON-ответ со всеми транзакциями, содержащими запрос в описании или категории,
        у которых в описании есть данная строка. Случай, когда строка отсутствует.'''

    # Устанавливаем возвращаемое значение для read_excel
    mock_read_excel.return_value = mock_data
    search = "Такси"
    expected = '[]'

    result = search_string_in_operations("path_to_file.xlsx", search)
    assert result == expected


@patch('pandas.read_excel')
def test_search_string_in_operations_failed(mock_read_excel):
    '''Тестирование функции, принимающей xlsx файл с данными о банковских операциях и строку поиска,
        вернулась ошибка.'''

    # Устанавливаем возвращаемое значение для read_excel
    mock_read_excel.return_value = None
    search = "Супермаркеты"

    with pytest.raises(Exception):
        assert search_string_in_operations("path_to_file.xlsx", search) == "Произошла ошибка:"
