import re

import requests
from bs4 import BeautifulSoup
from config import settings
USER_AGENT = settings.USER_AGENT

class VUZ_PARSER:
    @staticmethod
    def get_NSU(id: int,
            faculty: int = 8,
            direction: int = 6,
            condition: int = 10,
            type: int = 0
        ):
        # Создаем сессию (она будет сама держать куки)
        session = requests.Session()

        # Устанавливаем человеческие заголовки, чтобы прикинуться браузером
        session.headers.update({
            'User-Agent': USER_AGENT,
            'Referer': 'https://abiturient.nsu.ru/site/list',
        })

        # Шаг 1: Идем на страницу списков, чтобы забрать CSRF-токен
        main_page_url = 'https://abiturient.nsu.ru/site/list'
        response = session.get(main_page_url)

        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('meta', {'name': 'csrf-token'})['content']

        # Шаг 2: Готовим POST-запрос к эндпоинту
        api_url = 'https://abiturient.nsu.ru/site/list-content'

        # Добавляем токен в заголовки
        headers = {
            'X-CSRF-Token': csrf_token,
            'X-Requested-With': 'XMLHttpRequest' # Показывает серверу, что это AJAX-запрос
        }

        # Данные формы (передаем как x-www-form-urlencoded через аргумент data)
        payload = {
            '_csrf-frontend': csrf_token, # Дублируем токен в тело, Yii2 это любит
            'degree': 'bachelor',
            'faculty': faculty,
            'direction': direction,
            'condition': condition,
            'type': type
        }

        # Шаг 3: Делаем запрос
        api_response = session.post(api_url, data=payload, headers=headers)

        if api_response.status_code != 200:
            return None
        data = api_response.json()
        faculty = data['faculty']['name']
        total_places = data['info']['places']['total']['value']
        table_ngu = data['items'][2]['table']
        people_with_consent = 0
        kvota = len(data['items'][0]['table']) + len(data['items'][1]['table'])
        for i in table_ngu:
            if i['code'] == str(id):
                abiturient_number = i['number'] 
                break
            if i['consent'] == 'Да':
                people_with_consent += 1
        else:
            return None
        return (faculty, total_places, kvota, abiturient_number, people_with_consent)    

    @staticmethod
    def get_NSTU(id: int, url='https://www.nstu.ru/entrance/enrollment_campaign/rating_bachelor/entrance_list?comp_name=%D0%90%D0%92%D0%A2%D0%A4.1&fk_tr_basis=1'):
        session = requests.Session()
        session.headers.update({
            'User-Agent': USER_AGENT,
        })
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        places_div = soup.find('div', string="Количество бюджетных мест")
        cards = soup.find_all('div', class_='rating__card')

        people_with_consent = 0
        for card in cards:
            ord_num_tag = card.find('div', class_='rating__card__header-ordnum')
            position = ord_num_tag.text.strip() if ord_num_tag else "Не определено"
            id_tag = card.find('span', style="color:#51A2FF")
            user_id = id_tag.text.strip() if id_tag else "Не определено"

            priority_tag = card.find('div', class_='rating__table-cell__priority')
            priority = "Не определен"
            if priority_tag:
                priority = priority_tag.text.replace("Номер приоритета:", "").strip()
            
            consent_tag = card.find('div', class_="rating__table-cell__doc tablelike__table-cell")
            consert = consent_tag.text.replace("Наличие согласия на зачисление:", "").strip()
            if user_id == str(id):
                break
            if consert:
                people_with_consent += 1
        else:
            return None
        
        green_list_link = None
        green_anchor = soup.find(
            "span", string=re.compile("Если бы зачисление было сегодня")
        )
        if green_anchor:
            # Поднимаемся к родительскому тегу <a>, чтобы забрать href
            green_list_link = green_anchor.find_parent("a")["href"]
            # Если ссылка относительная (начинается с /), делаем её абсолютной
            if green_list_link.startswith("/"):
                green_list_link = "https://www.nstu.ru" + green_list_link

        green_position = None
        if green_list_link:
            green_response = session.get(green_list_link)
            green_soup = BeautifulSoup(green_response.text, "html.parser")

            # Ищем пользователя в зеленом списке (структура карточек там такая же)
            green_cards = green_soup.find_all("div", class_="rating__card")

            for card in green_cards:
                ord_num_tag = card.find('div', class_='rating__card__header-ordnum')
                green_position = ord_num_tag.text.strip() if ord_num_tag else "Не определено"
                id_tag = card.find('span', style="color:#51A2FF")
                user_id = id_tag.text.strip() if id_tag else "Не определено"
                consent_tag = card.find('div', class_="rating__table-cell__doc tablelike__table-cell")
                consert = consent_tag.text.replace("Наличие согласия на зачисление:", "").strip()
                if user_id == str(id):
                    break
            else:
                green_position = None
        return (position, green_position, people_with_consent)


