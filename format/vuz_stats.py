from urllib.parse import urlparse, parse_qs
from vuz_parser import VUZ_PARSER

def format_nsu_answer(user_code, competition_url):
    result_message = ''
    parsed_url = urlparse(competition_url)
    query_params = parse_qs(parsed_url.query)

    position = None
    try:
        faculty = int(query_params.get('faculty', ['8'])[0])
        direction = int(query_params.get('direction', ['6'])[0])
        condition = int(query_params.get('condition', ['10'])[0])
        type = int(query_params.get('type', ['0'])[0])
        
        nsu_data = VUZ_PARSER.get_NSU(
            id=user_code,
            faculty=faculty,
            direction=direction,
            condition=condition,
            type=type
        )
        if nsu_data:
            free_places, position, people_with_consent = nsu_data
            result_message += (
                f"Ваша статистика в конкурсе этого направления:"
                f"Всего бюджетных мест: {free_places}"
                f"Ваш номер: {position}"
                f"Человек с согласием до вас: {people_with_consent}"
            )
        else:
            result_message += "Не удалось получить данные для НГУ по этой ссылке. Возможно, пользователь не найден или ссылка некорректна."
    except (ValueError, KeyError) as e:
        result_message += f"Ошибка парсинга параметров для НГУ: {e}. Убедитесь, что ссылка корректна."
    return result_message, position


def format_nstu_answer(user_code, competition_url):
    result_message = ''
    position = None
    try:
        nstu_data = VUZ_PARSER.get_NSTU(id=user_code, url=competition_url)
        if nstu_data:
            free_places, position, people_with_consent = nstu_data
            result_message += (
                f"Ваша статистика в конкурсе этого направления:"
                f"Всего бюджетных мест: {free_places}"
                f"Ваш номер: {position}"
                f"Человек с согласием до вас: {people_with_consent}"
            )
        else:
            result_message += "Не удалось получить данные для НГТУ по этой ссылке. Возможно, пользователь не найден или ссылка некорректна."
    except Exception as e:
        result_message += f"Произошла ошибка при получении данных для НГТУ: {e}"
    if not position:
        position = None
    return result_message, position

def format_tgu_answer(user_code, competition_url):
    result_message = ''
    position = None
    try:
        tgu_data = VUZ_PARSER.get_TSU(id=user_code, url=competition_url)
        if tgu_data:
            free_places, position, people_with_consent = tgu_data
            result_message += (
                f"Ваша статистика в конкурсе этого направления:"
                f"Всего бюджетных мест: {free_places}"
                f"Ваш номер: {position}"
                f"Человек с согласием до вас: {people_with_consent}"
            )
        else:
            result_message += "Не удалось получить данные для ТГУ по этой ссылке. Возможно, пользователь не найден или ссылка некорректна."
    except Exception as e:
        result_message += f"Произошла ошибка при получении данных для ТГУ: {e}"
    if not position:
        position = None
    return result_message, position

def format_tpu_answer(user_code, competition_url):
    result_message = ''
    position = None
    try:
        tpu_data = VUZ_PARSER.get_TPU(id=user_code, url=competition_url)
        if tpu_data:
            free_places, position, people_with_consent = tpu_data
            result_message += (
                f"Ваша статистика в конкурсе этого направления:"
                f"Всего бюджетных мест: {free_places}"
                f"Ваш номер: {position}"
                f"Человек с согласием до вас: {people_with_consent}"
            )
        else:
            result_message += "Не удалось получить данные для ТПУ по этой ссылке. Возможно, пользователь не найден или ссылка некорректна."
    except Exception as e:
        result_message += f"Произошла ошибка при получении данных для ТПУ: {e}"
    if not position:
        position = None
    return result_message, position
