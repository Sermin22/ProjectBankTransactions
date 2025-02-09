import os
import re
import json
import pandas as pd
import logging


logger = logging.getLogger(__name__)
console_handler = logging.StreamHandler()
file_formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s: %(message)s')
console_handler.setFormatter(file_formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)


def search_string_in_operations(path_to_excel_file: str, search: str) -> str:
    '''Принимает xlsx файл с данными о банковских операциях и строку поиска,
    а возвращает JSON-ответ со всеми транзакциями, содержащими запрос в описании или категории,
    у которых в описании есть данная строка.'''

    try:
        # Преобразуем данные из excel файла в список словарей Python
        operations = pd.read_excel(path_to_excel_file).to_dict(orient='records')
        logger.info('Файл для поисковой строки преобразован')
        filtered_list_operations = []
        search = str(search)
        for operation in operations:
            for key, value in operation.items():
                matches = ""
                if key == "Категория" or key == "Описание":
                    value = str(value)
                    matches = re.findall(search, value, flags=re.IGNORECASE)
                if matches:
                    filtered_list_operations.append(operation)
        logger.info('Поиск по словам произведен')
        # Преобразуем словарь в строку JSON
        json_response = json.dumps(filtered_list_operations, ensure_ascii=False)
        logger.info('Вывод результата поиска')
        return json_response

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        logger.error('Произошла ошибка')
        return ""


if __name__ == '__main__':
    PATH_TO_FILE_XLSX = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "operations.xlsx")
    print(search_string_in_operations(PATH_TO_FILE_XLSX, "Zhenskiy Trikotazh"))
