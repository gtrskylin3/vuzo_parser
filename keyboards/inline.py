from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from models import UniversitiesDirections

def get_universities_keyboard(universities):
    builder = InlineKeyboardBuilder()
    for university in universities:
        builder.add(InlineKeyboardButton(text=university, callback_data=f"uni:{university}"))
    builder.add(InlineKeyboardButton(text="Назад", callback_data=f"back_menu"))
    builder.adjust(1)
    return builder.as_markup()

def get_add_competition_keyboard(directions: list[UniversitiesDirections], university_name):
    builder = InlineKeyboardBuilder()
    for direction in directions:
        builder.add(InlineKeyboardButton(text=f"{direction.name}", callback_data=f"view_dir:{direction.id}"))
    if len(directions) < 5:
        builder.add(InlineKeyboardButton(text="Добавить конкурс", callback_data=f"add_comp:{university_name}"))
    builder.add(InlineKeyboardButton(text="Назад", callback_data=f"back_menu"))
    builder.adjust(1)
    return builder.as_markup()

def get_start_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏘️ Начать", callback_data="start_registration")],
        [InlineKeyboardButton(text="👨‍🎓 Мой профиль", callback_data="my_profile")],

    ])
    return keyboard

def get_profile_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Изменить код", callback_data="update_code"))
    builder.add(InlineKeyboardButton(text="Назад", callback_data="start_registration"))
    builder.adjust(1)
    return builder.as_markup()