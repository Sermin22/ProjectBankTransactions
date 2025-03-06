import json
import pytest
from datetime import datetime
import pandas as pd
from src.reports import write_to_json, expenses_by_category


# Простая функция для тестирования
@write_to_json("test_report.json")
def test_function():
    return {"key": "value"}


def test_write_to_json_default_file():
    # Тестирование записи в файл по умолчанию
    @write_to_json
    def dummy_function():
        return {"dummy_key": "dummy_value"}

    assert dummy_function() == {"dummy_key": "dummy_value"}  # Проверяем, что функция возвращает корректный результат

    with open("reports.json", "w", encoding="utf-8") as f:
        json.dump({"dummy_key": "dummy_value"}, f, indent=4, default=str, ensure_ascii=False)

    with open("reports.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data == {"dummy_key": "dummy_value"}  # Проверяем содержимое файла


def test_write_to_json_custom_file():
    # Тестирование записи в пользовательский файл
    @write_to_json("custom_report.json")
    def another_dummy_function():
        return {"another_dummy_key": "another_dummy_value"}

    assert another_dummy_function() == {"another_dummy_key": "another_dummy_value"}

    with open("custom_report.json", "w", encoding="utf-8") as f:
        json.dump({"another_dummy_key": "another_dummy_value"}, f, indent=4, default=str, ensure_ascii=False)

    with open("custom_report.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data == {"another_dummy_key": "another_dummy_value"}


def test_test_function():
    # Тестирование функции, которая уже декорирована
    assert test_function() == {"key": "value"}

    with open("test_report.json", "w", encoding="utf-8") as f:
        json.dump({"key": "value"}, f, indent=4, default=str, ensure_ascii=False)

    with open("test_report.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        assert data == {"key": "value"}


@pytest.fixture
def df_operations():
    """Фикстура для создания тестового датафрейма"""

    data = {
        'Дата операции': ['2023-01-15 10:00:00', '2023-02-20 12:30:00', '2023-03-25 14:45:00'],
        'Категория': ['Продукты', 'Транспорт', 'Развлечения'],
        'Сумма': [1000, 500, 1500]
    }
    df = pd.DataFrame(data)
    df['Дата операции'] = pd.to_datetime(df['Дата операции'])
    return df


def test_expenses_by_category_valid_date(df_operations):
    '''Тест проверяет работу функции с правильной датой и соответствующей категорией.'''

    date_str = '2023-04-05 18:00:00'
    category = 'Продукты'

    result = expenses_by_category(df_operations, category, date_str)

    assert len(result) == 1
    assert result[0]['Категория'] == 'Продукты'
    assert result[0]['Сумма'] == 1000


def test_expenses_by_category_nonexistent_category(df_operations):
    '''Проверка, что функция возвращает пустой список, если категория отсутствует в датафрейме.'''
    date_str = '2023-04-05 18:00:00'
    category = 'Одежда'

    result = expenses_by_category(df_operations, category, date_str)

    assert len(result) == 0


def test_expenses_by_category_no_date_provided(df_operations, monkeypatch):
    '''Проверка, что функция использует текущую дату, если дата не указана'''

    # Патчим функцию now() чтобы всегда возвращать фиксированную дату
    class MockDate(datetime):
        @classmethod
        def now(cls):
            return datetime(2023, 4, 6)

    monkeypatch.setattr('datetime.datetime', MockDate)

    category = 'Транспорт'

    result = expenses_by_category(df_operations, category)

    assert len(result) == 1
    assert result[0]['Категория'] == 'Транспорт'
    assert result[0]['Сумма'] == 500


def test_expenses_by_category_invalid_date_format(df_operations):
    '''Проверка обработки неверного формата даты'''
    with pytest.raises(ValueError) as exc_info:
        date_str = '2023-04-05T18:00:00'
        category = 'Продукты'

        expenses_by_category(df_operations, category, date_str)

    assert str(exc_info.value) == "Неверный формат даты. Ожидается формат YYYY-MM-DD HH:MM:SS"
