import os
import pandas as pd
from datetime import datetime


def process_xlsx_file_with_date_filter(file_path, input_date_str):
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


def top_transactions_by_amount(file_path, input_date_str):
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


if __name__ == '__main__':
    PATH_TO_FILE_XLSX = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "operations.xlsx")

    input_date_str = '2021-12-31 16:44:00' # YYYY-MM-DD HH:MM:SS
    result = process_xlsx_file_with_date_filter(PATH_TO_FILE_XLSX, input_date_str)
    print(result)

    # input_date_str = '2021-12-31 16:44:00'  # YYYY-MM-DD HH:MM:SS
    # result = top_transactions_by_amount(PATH_TO_FILE_XLSX, input_date_str)
    # print(result)