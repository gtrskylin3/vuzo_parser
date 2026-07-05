from urllib.parse import urlparse, parse_qs
from vuz_parser import VUZ_PARSER

def format_nsu_answer(user_code, competition_url):
    result_message = ''
    parsed_url = urlparse(competition_url)
    query_params = parse_qs(parsed_url.query)

    try:
        faculty = int(query_params.get('faculty', ['8'])[0])
        direction = int(query_params.get('direction', ['6'])[0])
        condition = int(query_params.get('condition', ['10'])[0])
        type = int(query_params.get('type', ['0'])[0])
        position = None
        nsu_data = VUZ_PARSER.get_NSU(
            id=user_code,
            faculty=faculty,
            direction=direction,
            condition=condition,
            type=type
        )
        if nsu_data:
            faculty_name, total_places, kvota, position, people_with_consent = nsu_data
            result_message += (
                f"Ваша статистика в конкурсе этого направления ({faculty_name}):\n"
                f"Всего мест: {total_places}\n"
                f"Квота: {kvota}\n"
                f"Ваш номер: {position}\n"
                f"Человек с согласием: {people_with_consent}\n"
            )
        else:
            result_message += "Не удалось получить данные для НГУ по этой ссылке.\n"
    except (ValueError, KeyError) as e:
        result_message += f"Ошибка парсинга параметров для НГУ: {e}. Убедитесь, что ссылка корректна.\n"
    except Exception as e:
        result_message += f"Произошла ошибка при получении данных для НГУ: {e}\n"
    return result_message, position


def format_nstu_answer(user_code, competition_url):
    result_message = ''
    try:
        nstu_data = VUZ_PARSER.get_NSTU(id=user_code, url=competition_url)
        if nstu_data:
            position, green_position, people_with_consent = nstu_data
            result_message += (
                f"Ваша позиция в общем списке НГТУ: {position}\n"
                f"Ваша позиция в 'зеленом' списке НГТУ: {green_position}\n"
                f"Человек с согласием (НГТУ): {people_with_consent}\n"
            )
        else:
            result_message += "Не удалось получить данные для НГТУ по этой ссылке.\n"
    except Exception as e:
        result_message += f"Произошла ошибка при получении данных для НГТУ: {e}\n"
    if not position:
        position = None
    return result_message, position