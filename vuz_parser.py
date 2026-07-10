import re
import requests
from bs4 import BeautifulSoup
from config import settings
import os

USER_AGENT = settings.USER_AGENT
TEMP_DIR = "C://Users//daniil//.gemini//tmp//vuzo-parser"

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
    def get_NSTU(id: int, url='https://www.nstu.ru/entrance/enrollment_campaign/rating_bachelor/entrance_list?competition=10581&fk_tr_basis=1&o_only=0'):
        session = requests.Session()
        session.headers.update({
            'User-Agent': USER_AGENT,
        })
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Request failed or timed out: {e}")
            return None
            
        soup = BeautifulSoup(response.text, 'html.parser')
        total_budget_places = 0
        places_text_tag = soup.find(string=re.compile("Количество бюджетных мест"))
        if places_text_tag:
            # The number is usually in the next sibling.
            next_sibling = places_text_tag.find_next_sibling()
            if next_sibling and next_sibling.name == 'strong': # If it's in a strong tag
                total_budget_places = int(next_sibling.text.strip())
            else: # Otherwise, try to extract from the parent or text itself
                match = re.search(r'(\d+)', places_text_tag.parent.text)
                if match:
                    total_budget_places = int(match.group(1))
        
        cards = soup.find_all('div', class_='rating__card')

        people_with_consent_above = 0
        for card in cards:
            ord_num_tag = card.find('div', class_='rating__card__header-ordnum')
            position = int(ord_num_tag.text.strip()) if ord_num_tag else None
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
                people_with_consent_above += 1
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
                green_position = int(ord_num_tag.text.strip()) if ord_num_tag else None
                id_tag = card.find('span', style="color:#51A2FF")
                user_id = id_tag.text.strip() if id_tag else "Не определено"
                consent_tag = card.find('div', class_="rating__table-cell__doc tablelike__table-cell")
                consert = consent_tag.text.replace("Наличие согласия на зачисление:", "").strip()
                if user_id == str(id):
                    break
            else:
                green_position = None
        return (position, green_position, people_with_consent_above, total_budget_places)

    @staticmethod
    def get_TSU(id: int, url='https://ratings.tsu.ru/study_stage/programs/bachelor/group-ratings/78167d23-de01-4d26-8f9e-d9e41bc9beb0'):
        session = requests.Session()
        session.headers.update({
            'User-Agent': USER_AGENT,
        })
        response = session.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract total budget places
        budget_places_tag = soup.find(string=re.compile(r'Всего бюджетных мест:'))
        total_budget_places = 0
        if budget_places_tag:
            total_budget_places = int(budget_places_tag.find_next('strong').text.strip())

        # Find the table with the students
        table = soup.find('table', class_='table')
        if not table:
            return None
            
        # Find the person in the table and count people with consent above
        people_with_consent_above = 0
        user_found = False
        
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if cells and len(cells) > 1:
                current_id = cells[1].text.strip()
                consent_text = cells[9].text.strip()
                
                if current_id == str(id):
                    user_found = True
                    position = int(cells[0].text.strip())
                    konkurs_ball = int(cells[6].text.strip())
                    soglasie = 'Да' in consent_text
                    priority = int(cells[7].text.strip())
                    bvi = 'Да' in cells[10].text
                    
                    return (
                        total_budget_places,
                        position,
                        people_with_consent_above,
                        konkurs_ball,
                        soglasie,
                        priority,
                        bvi
                    )
                
                if not user_found and 'Да' in consent_text:
                    people_with_consent_above += 1
        return None

    @staticmethod
    def get_TPU(id: int, competition_id=2336):
        session = requests.Session()
        session.headers.update({
            'User-Agent': USER_AGENT,
        })

        # Get header information
        header_url = f'https://apply.tpu.ru/api/competition/header?competition_id={competition_id}'
        header_response = session.get(header_url)
        if header_response.status_code != 200:
            return None
        header_data = header_response.json()
        total_budget_places = int(header_data['body']['data']['mest'])

        # Get all students
        students = []
        page = 0
        while True:
            list_url = f'https://apply.tpu.ru/api/entity/view?slug=competitive_group_list&admission_condition_id=924&place_type_id=6&all_prioritet=1&dok_vid=0&per-page=10&page={page}'
            list_response = session.get(list_url)
            if list_response.status_code != 200:
                return None
            list_data = list_response.json()['body']
            students.extend(list_data['data'])
            if len(students) >= list_data['total']:
                break
            page += 1

        # Find the user and people with consent above
        people_with_consent_above = 0
        user_found = False
        position = 0
        for i, student in enumerate(students):
            position = i + 1
            if student['unique_code_profile'] == str(id):
                user_found = True
                konkurs_ball = int(student['summar_ball'])
                soglasie = student['status_dok_label'] == 'Электронное'
                priority = int(student['prioritet'])
                status = student['status_label']
                
                return (
                    total_budget_places,
                    position,
                    people_with_consent_above,
                    konkurs_ball,
                    soglasie,
                    priority,
                    status
                )
            
            if not user_found and student['status_dok_label'] == 'Электронное':
                people_with_consent_above += 1
        
        return None
