import os
import pandas as pd
from datetime import datetime, time
from dotenv import load_dotenv
import requests


def greet_by_time(datetime_str: str) -> str:
    '''Функция принимает на вход строку с датой и временем в формате YYYY-MM-DD HH:MM:SS
    и в зависимости от времени дня выводит приветствие'''

    # Преобразуем строку в объект datetime
    dt = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

    # Определяем начало и конец каждого временного интервала
    morning_start = time(6, 0, 0)
    day_start = time(12, 0, 0)
    evening_start = time(18, 0, 0)
    night_start = time(0, 0, 0)
    time_max = time(23, 59, 59)  # можно в условии заменить на time.max

    # Получаем текущее время
    current_time = dt.time()
    # Сравнения с временными интервалами
    greeting = ''
    if morning_start <= current_time < day_start:
        greeting = 'Доброе утро'
    elif day_start <= current_time < evening_start:
        greeting = 'Добрый день'
    elif evening_start <= current_time < time_max:
        greeting = 'Добрый вечер'
    elif night_start <= current_time < morning_start:
        greeting = 'Доброй ночи'
    # можно еще эти строки, вместо двух последних elif:
    # elif evening_start <= current_time < time.max:
    #     greeting = 'Добрый вечер'
    # else:
    #     greeting = 'Доброй ночи'
    return greeting


def process_xlsx_file_with_date_filter(file_path: str, input_date_str: str) -> list[dict]:
    '''Принимает на вход файла xlsx, преобразует в DataFrame, отфильтровывает по дате операций - конечная дата
    это дата принимается функцией в качестве аргумента в виде строки, а начальная дата - это первый день месяца
    конечной даты. Группиррует по номеру карты и агрегирует суммы платежей и кэшбека c получением абсолютного
    значения суммы платежей. Возвращает список словарей'''

    # Чтение данных из файла xlsx
    df = pd.read_excel(file_path, parse_dates=['Дата операции'],
                       date_format='%d.%m.%Y %H:%M:%S')
    # Замена всех NaN значений на 0
    df.fillna(0, inplace=True)
    # Преобразуем строку с датой в формат datetime
    input_date = datetime.strptime(input_date_str, '%Y-%m-%d %H:%M:%S')
    # Определяем начало месяца
    start_of_month = input_date.replace(day=1, hour=0, minute=0, second=0)
    # Фильтруем данные по диапазону дат
    filtered_df = df[(df['Дата операции'] >= start_of_month) & (df['Дата операции'] <= input_date)]
    # Исключение строк, где сумма платежа больше нуля
    exclusion_of_positive_amounts = filtered_df.query("`Сумма платежа` < 0")
    # Группировка по номеру карты и агрегирование суммы платежей и кэшбека c получением
    # абсолютного значения суммы платежей
    grouped_df = exclusion_of_positive_amounts.groupby(['Номер карты']).agg({
        'Сумма платежа': lambda x: abs(x.sum()),
        'Кэшбэк': 'sum'
    }).reset_index()
    # Преобразование DataFrame в список словарей
    list_dict = grouped_df.to_dict('records')
    return list_dict


def top_transactions_by_amount(file_path: str, input_date_str: str) -> list[dict]:
    '''Принимает на вход файла xlsx, преобразует в DataFrame, отфильтровывает по дате операций - конечная дата
    это дата принимается функцией в качестве аргумента в виде строки, а начальная дата - это первый день месяца
    конечной даты. Возвращает список со словарями топ-5 транзакций по сумме платежа'''

    # Чтение данных из файла xlsx
    df = pd.read_excel(file_path, parse_dates=['Дата операции'], date_format='%d.%m.%Y %H:%M:%S')
    # Замена всех NaN значений на 0
    df.fillna(0, inplace=True)
    # Преобразуем строку с датой в формат datetime
    input_date = datetime.strptime(input_date_str, '%Y-%m-%d %H:%M:%S')
    # Определяем начало месяца
    start_of_month = input_date.replace(day=1, hour=0, minute=0, second=0)
    # Фильтруем данные по диапазону дат
    filtered_df = df[(df['Дата операции'] >= start_of_month) & (df['Дата операции'] <= input_date)]
    # Исключение строк, где сумма платежа больше нуля
    exclusion_of_positive_amounts = filtered_df.query("`Сумма платежа` < 0")
    # Применяем abs() к столбцу 'Сумма операции'
    exclusion_of_positive_amounts.loc[:, 'Сумма платежа'] = exclusion_of_positive_amounts['Сумма платежа'].apply(abs)
    # Сортируем DataFrame по убыванию суммы операции
    sorted_df = exclusion_of_positive_amounts.sort_values(by=['Сумма платежа'], ascending=False)
    # Ограничиваемся первыми пятью строками и нужными столбцами
    top_5_rows = sorted_df[['Дата операции', 'Сумма платежа', 'Категория', 'Описание']].head(5)
    # Преобразуем дату в обычный строковый формат
    top_5_rows['Дата операции'] = top_5_rows['Дата операции'].dt.strftime('%d.%m.%Y')
    # Преобразуем DataFrame в список словарей
    result_list = top_5_rows.to_dict('records')
    return result_list


def stock_prices() -> list[dict]:
    '''Происходит обращение к внешнему API для получения текущей стоимости акций из S&P500'''

    # Загрузка переменных окружения из файла .env
    load_dotenv()
    API_Key_marketstack = os.getenv('API_Key_marketstack')

    if not API_Key_marketstack:
        raise ValueError("Ключ API не задан в среде.")

    try:
        # Формирование URL для запроса к API
        url = f"https://api.marketstack.com/v2/eod?access_key={API_Key_marketstack}"
        # Параметры запроса (символы акций)
        querystring = {"symbols": "AAPL,AMZN,GOOGL,MSFT,TSLA"}
        # Отправка GET-запроса
        response = requests.get(url, params=querystring)
        # Проверяем успешность запроса
        if response.status_code != 200:
            raise Exception(f"Запрос не выполнен с кодом состояния: {response.status_code}")
        # Преобразование ответа в JSON
        data = response.json()
        # Извлекаем нужные данные
        list_dict_data = []
        for item in data['data']:
            list_dict_data.append({
                'symbol': item['symbol'],
                'close': item['close']
            })
        result = list_dict_data[0:5]
        return result

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []


def recent_currency_rates() -> list[dict]:
    '''Происходит обращение к внешнему API для получения текущекурса USD и EUR'''

    # Загрузка переменных окружения из файла .env
    load_dotenv()
    APIlayer_KEY = os.getenv('APIlayer_KEY')

    if not APIlayer_KEY:
        raise ValueError("Ключ API не задан в среде.")

    headers = {
        "apikey": APIlayer_KEY
    }
    try:
        # Формирование URL для запроса к API
        url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={"USD,EUR"}"
        response = requests.get(url, headers=headers)
        # Проверяем успешность запроса
        if response.status_code != 200:
            raise Exception(f"Запрос не выполнен с кодом состояния: {response.status_code}")

        rates = response.json()['rates']
        # Создаём пустой список для хранения результатов
        result = []
        # Извлекаем данные курсов валют
        for currency, rate in rates.items():
            result.append({
                'currency': currency,
                'rate': rate
            })
        return result

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []


if __name__ == '__main__':
    # PATH_TO_FILE_XLSX = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "operations.xlsx")

    # print(greet_by_time('2023-10-01 07:15:00'))  # Доброе утро
    # print(greet_by_time('2023-10-01 13:30:00'))  # Добрый день
    # print(greet_by_time('2023-10-01 19:45:00'))  # Добрый вечер
    # print(greet_by_time('2023-10-01 02:20:00'))  # Доброй ночи
    #
    # input_date_str = '2021-12-31 16:44:00' # YYYY-MM-DD HH:MM:SS
    # result = process_xlsx_file_with_date_filter(PATH_TO_FILE_XLSX, input_date_str)
    # print(result)

    # input_date_str = '2021-12-31 16:44:00'  # YYYY-MM-DD HH:MM:SS
    # result = top_transactions_by_amount(PATH_TO_FILE_XLSX, input_date_str)
    # print(result)

    # print(stock_prices())
    print(recent_currency_rates())
