import requests
import pandas as pd
from io import BytesIO

def url_connect(url):
    try:
        # Отправляем GET-запрос к URL и автоматически закрываем сессию после получения ответа
        with requests.get(url) as response:
            # Проверяем статус ответа и генерируем исключение при неуспешном ответе
            response.raise_for_status()
            
            # Используем BytesIO для чтения из байтовой строки
            excel_data = BytesIO(response.content)
            
            # Список необходимых столбцов
            columns = ['Название объекта', 'Краткое наименование', 'Очередь', 'Этап', 'Дом']
            
            # Читаем Excel-файл, выбираем необходимую вкладку и фильтруем по столбцам
            df = pd.read_excel(excel_data, sheet_name="Сводная таблица", usecols=columns)
            
            return df
    except requests.HTTPError as e:
        return f"Ошибка HTTP: {e}"
    except requests.ConnectionError:
        return "Ошибка подключения. Пожалуйста, проверьте ваше соединение с интернетом."
    except Exception as e:
        return f"Произошла непредвиденная ошибка: {e}"
