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
    return result_message, position, total_places


def format_nstu_answer(user_code, competition_url):
    result_message = ''
    try:
        nstu_data = VUZ_PARSER.get_NSTU(id=user_code, url=competition_url)
        print(nstu_data)
        if nstu_data:
            position, green_position, people_with_consent, free_places = nstu_data
            result_message += (
                f"Количество бюджетных мест: {free_places}\n"
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
    return result_message, position, free_places


def format_tgu_answer(user_code, competition_url):
    result_message = ''
    position = None
    try:
        tgu_data = VUZ_PARSER.get_TSU(id=user_code, url=competition_url)
        if tgu_data:
            total_budget_places, position, people_with_consent_above, konkurs_ball, soglasie, priority, bvi = tgu_data
            result_message += (
                f"Ваша статистика в конкурсе ТГУ:\n"
                f"Всего бюджетных мест: {total_budget_places}\n"
                f"Ваша позиция: {position}\n"
                f"Человек с согласием выше: {people_with_consent_above}\n"
                f"Конкурсный балл: {konkurs_ball}\n"
                f"Согласие на зачисление: {'Да' if soglasie else 'Нет'}\n"
                f"Приоритет: {priority}\n"
                f"БВИ: {'Да' if bvi else 'Нет'}\n"
            )
        else:
            result_message += "Не удалось получить данные для ТГУ по этой ссылке.\n"
    except (ValueError, KeyError) as e:
        result_message += f"Ошибка парсинга параметров для ТГУ: {e}. Убедитесь, что ссылка корректна.\n"
    except Exception as e:
        result_message += f"Произошла ошибка при получении данных для ТГУ: {e}\n"
    return result_message, position, total_budget_places


def format_tpu_answer(user_code, competition_url):
    result_message = ''
    position = None
    try:
        parsed_url = urlparse(competition_url)
        query_params = parse_qs(parsed_url.query)
        competition_id = int(query_params.get('competition_id', ['0'])[0])

        tpu_data = VUZ_PARSER.get_TPU(id=user_code, competition_id=competition_id)
        if tpu_data:
            total_budget_places, position, people_with_consent_above, konkurs_ball, soglasie, priority, status = tpu_data
            result_message += (
                f"Ваша статистика в конкурсе ТПУ:\n"
                f"Всего бюджетных мест: {total_budget_places}\n"
                f"Ваша позиция: {position}\n"
                f"Человек с согласием выше: {people_with_consent_above}\n"
                f"Конкурсный балл: {konkurs_ball}\n"
                f"Согласие на зачисление: {'Да' if soglasie else 'Нет'}\n"
                f"Приоритет: {priority}\n"
                f"Статус: {status}\n"
            )
        else:
            result_message += "Не удалось получить данные для ТПУ по этой ссылке.\n"
    except (ValueError, KeyError) as e:
        result_message += f"Ошибка парсинга параметров для ТПУ: {e}. Убедитесь, что ссылка корректна и содержит competition_id.\n"
    except Exception as e:
        result_message += f"Произошла ошибка при получении данных для ТПУ: {e}\n"
    return result_message, position, total_budget_places