import pytest
from vuz_parser import VUZ_PARSER

# def test_get_nsu():
#     data = VUZ_PARSER.get_NSU(id=1316927)
#     assert data is not None
#     faculty, total_places, kvota, abiturient_number, people_with_consent = data
#     assert faculty == "Факультет информационных технологий"
#     assert total_places == 125
#     assert kvota == 37
#     assert int(abiturient_number) == 900
#     assert people_with_consent == 78

def test_get_nstu():
    data = VUZ_PARSER.get_NSTU(id=1138998)
    print(data)
    
# def test_get_tsu():
#     data = VUZ_PARSER.get_TSU(id=1248706)
#     assert data is not None
#     total_budget_places, position, people_with_consent_above, konkurs_ball, soglasie, priority, bvi = data
#     assert total_budget_places == 21
#     assert position == 1
#     assert people_with_consent_above == 0
#     assert konkurs_ball == 199
#     assert soglasie == True
#     assert priority == 1
#     assert bvi == False

# def test_get_tpu():
#     # Test with a user on the first page
#     data = VUZ_PARSER.get_TPU(id=988633)
#     assert data is not None
#     total_budget_places, position, people_with_consent_above, konkurs_ball, soglasie, priority, status = data
#     assert total_budget_places == 40
#     assert position == 1
#     assert people_with_consent_above == 0
#     assert konkurs_ball == 213
#     assert soglasie == True
#     assert priority == 1
#     assert status == "Участвует в конкурсе"

#     # Test with a user on another page to test pagination
#     data = VUZ_PARSER.get_TPU(id=1680667)
#     assert data is not None
#     total_budget_places, position, people_with_consent_above, konkurs_ball, soglasie, priority, status = data
#     assert total_budget_places == 40
#     assert position == 10
#     assert people_with_consent_above == 1
#     assert konkurs_ball == 264
#     assert soglasie == False
#     assert priority == 1
#     assert status == "Участвует в конкурсе"
