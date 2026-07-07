from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    waiting_for_code = State()
    waiting_for_university = State()
    waiting_for_direction_name = State()
    waiting_for_url = State()
    viewing_university = State()
    updating_code = State()
