import pandas as pd
import datetime
import json
import logging
import os
from functools import wraps

logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
file_formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s: %(message)s')
console_handler.setFormatter(file_formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)


def write_to_json(file_name="reports.json"):
    """Декоратор для записи результата функции в файл в формате JSON."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            with open(file_name, "w", encoding="utf-8") as file:
                json.dump(result, file, default=str, ensure_ascii=False, indent=4)

            return result

        return wrapper

    if callable(file_name):
        func = file_name
        file_name = "reports.json"
        return decorator(func)
    return decorator


# @write_to_json
# @write_to_json("parameter_reports.json")
def expenses_by_category(df_operations, category, date_str=None):
    '''Функция принимает на вход датафрейм с транзакциями, название категории, опциональную дату.
    Если дата не передана, то берется текущая дата. Функция возвращает траты по заданной категории
    за последние три месяца (от переданной даты).'''

    try:
        if date_str is not None:
            try:
                date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValueError("Неверный формат даты. Ожидается формат YYYY-MM-DD HH:MM:SS")
        else:
            date = datetime.datetime.now()

        logger.info('Начальная дата для фильтрации транзакций получена')
        # Определяем начальную дату трех месяцев назад
        start_date = date - datetime.timedelta(days=90)
        # Преобразуем столбец 'Дата операции' в формат datetime с указанием формата
        df_operations['Дата операции'] = pd.to_datetime(df_operations['Дата операции'], format='%d.%m.%Y %H:%M:%S')
        # Фильтруем данные по дате и категории
        df_filtered = df_operations.query(
            f'Категория == "{category}" & `Дата операции` >= @start_date & `Дата операции` <= @date',
            local_dict={'start_date': start_date, 'date': date})
        # Преобразуем датафрейм в список словарей
        logger.info('Фильтрации транзакций за последние 90 дней произведена')
        result_list = df_filtered.to_dict('records')
        # Преобразуем результат в JSON
        json_result = json.dumps(result_list, indent=4, default=str, ensure_ascii=False)
        logger.info('Транзакции за последние 90 дней получены')
        return json_result

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        logger.error('Произошла ошибка')
        return ""


if __name__ == '__main__':
    PATH_TO_FILE_XLSX = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "operations.xlsx")
#     df = pd.read_excel(PATH_TO_FILE_XLSX)
#     print(expenses_by_category(df, 'Супермаркеты', '2021-12-31 07:15:00'))
#     print(expenses_by_category(df, 'Каршеринг', '2021-11-01 13:30:00'))
#     print(expenses_by_category(df, 'Канцтовары'))
