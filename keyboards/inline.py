from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_universities_keyboard(universities):
    builder = InlineKeyboardBuilder()
    for university in universities:
        builder.add(InlineKeyboardButton(text=university, callback_data=f"uni:{university}"))
    builder.adjust(1)
    return builder.as_markup()

def get_add_competition_keyboard(university_name):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Добавить конкурс", callback_data=f"add_comp:{university_name}"))
    return builder.as_markup()
