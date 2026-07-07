import re
import requests
from bs4 import BeautifulSoup, Tag
from config import settings
from loguru import logger
from urllib.parse import urljoin

USER_AGENT = settings.USER_AGENT


class VUZ_PARSER:
    @staticmethod
    def get_NSU(id: int, faculty: int = 8, direction: int = 6, condition: int = 10, type: int = 0):
        logger.info(f"Starting NSU parser for user {id}")
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": USER_AGENT,
                "Referer": "https://abiturient.nsu.ru/site/list",
            }
        )
        try:
            main_page_url = "https://abiturient.nsu.ru/site/list"
            response = session.get(main_page_url)
            # Do not raise for status here, as a 400 is expected by the user

            soup = BeautifulSoup(response.text, "html.parser")
            csrf_token_tag = soup.find("meta", {"name": "csrf-token"})
            if not isinstance(csrf_token_tag, Tag) or not csrf_token_tag.has_attr("content"):
                logger.error("NSU parser: CSRF token not found.")
                return None
            csrf_token = csrf_token_tag["content"]

            api_url = "https://abiturient.nsu.ru/site/list-content"
            headers = {
                "X-CSRF-Token": csrf_token,
                "X-Requested-With": "XMLHttpRequest",
            }
            payload = {
                "_csrf-frontend": csrf_token,
                "degree": "bachelor",
                "faculty": faculty,
                "direction": direction,
                "condition": condition,
                "type": type,
            }

            api_response = session.post(api_url, data=payload, headers=headers)
            api_response.raise_for_status()
            data = api_response.json()

            table_nsu = None
            free_places = 0
            for item in data.get("items", []):
                if item.get("title") == "общий конкурс":
                    table_nsu = item.get("table")
                    free_places = item.get("info", {}).get("place", {}).get("total", {}).get("value", 0)
                    break

            if table_nsu is None:
                logger.warning(f"NSU parser: 'общий конкурс' table not found for user {id}.")
                return None

            position = -1
            consent_before = 0

            if not isinstance(table_nsu, list):
                return None

            for person in table_nsu:
                if person.get("code") == str(id):
                    position = int(person.get("number", -1))
                    break
                if person.get("consent") == "Да":
                    consent_before += 1
            else:
                logger.warning(f"NSU parser: User {id} not found in the list.")
                return None

            logger.success(f"NSU parser successful for user {id}. Position: {position}")
            return (free_places, position, consent_before)

        except requests.RequestException as e:
            logger.error(f"NSU parser network error for user {id}: {e}")
            return None
        except (KeyError, AttributeError, ValueError) as e:
            logger.error(f"NSU parser data parsing error for user {id}: {e}")
            return None

    @staticmethod
    def get_NSTU(id: int, url: str):
        logger.info(f"Starting NSTU parser for user {id}, URL: {url}")
        session = requests.Session()
        session.headers.update({"User-Agent": USER_AGENT})
        base_url = "https://www.nstu.ru"

        try:
            initial_response = session.get(url)
            initial_response.raise_for_status()
            initial_soup = BeautifulSoup(initial_response.text, "html.parser")

            general_competition_link_tag = initial_soup.find("a", string=re.compile(r"На общих основаниях"))
            if not isinstance(general_competition_link_tag, Tag) or not general_competition_link_tag.has_attr('href'):
                soup = initial_soup
            else:
                href = general_competition_link_tag['href']
                if not isinstance(href, str):
                    return None
                
                general_competition_url = urljoin(base_url, href)
                
                logger.debug(f"NSTU parser: Found general competition link: {general_competition_url}")
                response = session.get(general_competition_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

            free_places = 0
            places_node = soup.find(string=re.compile(r"Количество бюджетных мест"))
            if places_node:
                parent = places_node.find_parent("div")
                text_to_search = parent.get_text() if parent else str(places_node)
                match = re.search(r"\d+", text_to_search)
                if match:
                    free_places = int(match.group(0))

            cards = soup.find_all("div", class_="rating__card")
            consent_before = 0
            position = -1

            for card in cards:
                id_tag = card.find("span", style="color:#51A2FF")
                user_id = id_tag.text.strip() if id_tag else None

                if user_id == str(id):
                    ord_num_tag = card.find("div", class_="rating__card__header-ordnum")
                    if ord_num_tag and ord_num_tag.text.strip().isdigit():
                        position = int(ord_num_tag.text.strip())
                    break

                consent_tag = card.find("div", class_="rating__table-cell__doc tablelike__table-cell")
                if consent_tag and "Да" in consent_tag.get_text():
                    consent_before += 1

            if position == -1:
                logger.warning(f"NSTU parser: User {id} not found at URL {url}.")
                return None

            logger.success(f"NSTU parser successful for user {id}. Position: {position}")
            return (free_places, position, consent_before)

        except requests.RequestException as e:
            logger.error(f"NSTU parser network error for user {id}: {e}")
            return None
        except (KeyError, AttributeError, IndexError) as e:
            logger.error(f"NSTU parser data parsing error for user {id}: {e}")
            return None

    @staticmethod
    def get_TSU(id: int, url: str):
        logger.info(f"Starting TSU parser for user {id}, URL: {url}")
        session = requests.Session()
        session.headers.update({"User-Agent": USER_AGENT})

        try:
            response = session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")

            free_places = 0
            competition_button = soup.find(
                "div", class_="card-header", attrs={"data-toggle": "collapse", "href": "#collapse-GeneralCompetition-Budget"}
            )
            if competition_button:
                match = re.search(r"Бюджет (\d+) мест", competition_button.get_text())
                if match:
                    free_places = int(match.group(1))

            table_container = soup.find("div", id="collapse-GeneralCompetition-Budget")
            if not isinstance(table_container, Tag):
                logger.warning(f"TSU parser: Competition table container not found for user {id} at {url}.")
                return None

            table = table_container.find("table")
            if not isinstance(table, Tag):
                logger.warning(f"TSU parser: Competition table not found for user {id} at {url}.")
                return None
            
            tbody = table.find("tbody")
            if not isinstance(tbody, Tag):
                logger.warning(f"TSU parser: Competition table body not found for user {id} at {url}.")
                return None

            rows = tbody.find_all("tr")
            position = -1
            consent_before = 0

            for i, row in enumerate(rows):
                cols = row.find_all("td")
                if not cols or len(cols) < 9:
                    continue

                user_id_tag = cols[1]
                user_id = user_id_tag.text.strip()

                if user_id == str(id):
                    position_tag = cols[0]
                    position = int(position_tag.text.strip())
                    break

                consent_tag = cols[8]
                if "Да" in consent_tag.get_text():
                    consent_before += 1

            if position == -1:
                logger.warning(f"TSU parser: User {id} not found at URL {url}.")
                return None

            logger.success(f"TSU parser successful for user {id}. Position: {position}")
            return (free_places, position, consent_before)

        except requests.RequestException as e:
            logger.error(f"TSU parser network error for user {id}: {e}")
            return None
        except (KeyError, AttributeError, IndexError, ValueError) as e:
            logger.error(f"TSU parser data parsing error for user {id}: {e}")
            return None

    @staticmethod
    def get_TPU(id: int, url: str):
        logger.info(f"Starting TPU parser for user {id}, URL: {url}")
        session = requests.Session()
        session.headers.update({"User-Agent": USER_AGENT})

        try:
            competition_id = url.split("/")[-1]
            header_url = f"https://apply.tpu.ru/api/competition/header?competition_id={competition_id}"

            header_response = session.get(header_url)
            header_response.raise_for_status()
            header_data = header_response.json()

            free_places = 0
            competition_info = None

            for comp in header_data.get("body", {}).get("data", {}).get("competition_list", []):
                if comp.get("short_name") == "Основные места в рамках КЦП":
                    competition_info = comp
                    break

            if not competition_info:
                logger.warning(f"TPU parser: Main competition info not found for user {id} at {url}.")
                return None

            free_places = int(header_data.get("body", {}).get("data", {}).get("mest", 0))
            admission_condition_id = competition_info["admission_condition_id"]
            place_type_id = competition_info["place_type_id"]

            api_url = f"https://apply.tpu.ru/api/entity/view?slug=competitive_group_list&admission_condition_id={admission_condition_id}&place_type_id={place_type_id}&all_prioritet=1&dok_vid=0&per-page=1000"

            api_response = session.get(api_url)
            api_response.raise_for_status()
            data = api_response.json()

            position = -1
            consent_before = 0
            
            data_list = data.get("body", {}).get("data", [])
            if not isinstance(data_list, list):
                return None

            for i, student in enumerate(data_list):
                if student.get("unique_code_profile") == str(id):
                    position = i + 1
                    break
                if student.get("status_label") == "Участвует в конкурсе":
                    consent_before += 1

            if position == -1:
                logger.warning(f"TPU parser: User {id} not found at URL {url}.")
                return None

            logger.success(f"TPU parser successful for user {id}. Position: {position}")
            return (free_places, position, consent_before)

        except requests.RequestException as e:
            logger.error(f"TPU parser network error for user {id}: {e}")
            return None
        except (KeyError, AttributeError, IndexError, ValueError) as e:
            logger.error(f"TPU parser data parsing error for user {id}: {e}")
            return None
