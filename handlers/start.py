from aiogram import Router, F
from aiogram.types import FSInputFile, Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from format import vuz_stats
from repository.universities import UniversitiesRepository
from states import Form
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.inline import (
    get_universities_keyboard,
    get_add_competition_keyboard,
    get_start_keyboard,
    get_profile_keyboard,
)
from vuz_parser import VUZ_PARSER
from repository.users import UsersRepository
from config import BASE_DIR, UNIVERSITIES
import utils.handlers as utils

router = Router()

@router.message(Command("start"))
@router.callback_query(F.data == "back_menu")
async def command_start(event: Message | CallbackQuery):
    callback = None
    if isinstance(event, Message):
        message = event
    if isinstance(event, CallbackQuery):
        message = event.message
        callback = True
    await message.answer_photo(
        photo=FSInputFile(BASE_DIR / "icon.png"),
        caption="""Привет! Я бот для отслеживания твоей позиции в конкурсных списках ВУЗа.
Я умею работать со списками, где есть твой уникальный код.""",
        parse_mode="Markdown",
        reply_markup=get_start_keyboard(),
    )
    if callback:
        await event.answer()

@router.callback_query(F.data == "my_profile")
async def my_profile(
    callback: CallbackQuery,
    user_repo: UsersRepository,
    univer_repo: UniversitiesRepository,
    state: FSMContext,
):
    user = await user_repo.get_or_create_user(callback.from_user.id)
    if not user.user_code:
        await callback.message.answer(
            "Вы еще не зарегистрированы. Введите свой код, по которому можно отследить позицию в конкурсе:"
        )
        await state.set_state(Form.waiting_for_code)
        await callback.answer()
        return

    total_vuz, vuz_stats = await univer_repo.get_user_stats(user.id)

    stats_lines = [
        f"— Вуз: {vuz_name}, направлений: {count}/5"
        for vuz_name, count in vuz_stats.items()
    ]
    stats_str = "\n".join(stats_lines)

    await callback.message.answer(
        f"""**Ваш профиль**
**Ваш код:** `{user.user_code}`
**Добавлено ВУЗов:** {total_vuz}
{stats_str}
""",
        reply_markup=get_profile_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()


@router.callback_query(F.data == "update_code")
async def update_code(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новый код")
    await state.set_state(Form.updating_code)
    await callback.answer()


@router.message(Form.updating_code)
async def process_updating_code(
    message: Message,
    state: FSMContext,
    user_repo: UsersRepository,
    univer_repo: UniversitiesRepository,
):
    await state.clear()
    user = await user_repo.update_user_code(message.from_user.id, message.text)
    total_vuz, vuz_stats = await univer_repo.get_user_stats(user.id)

    stats_lines = [
        f"— Вуз: {vuz_name}, направлений: {count}/5"
        for vuz_name, count in vuz_stats.items()
    ]
    stats_str = "\n".join(stats_lines)
    await message.answer(
        f"""Ваш код успешно обновлен!

**Ваш профиль**
**Ваш код:** `{user.user_code}`
**Добавлено ВУЗов:** {total_vuz}
{stats_str}
""",
        reply_markup=get_profile_keyboard(),
        parse_mode="Markdown"
    )



@router.callback_query(F.data.startswith("start_registration"))
async def start_dialog(
    callback: CallbackQuery,
    state: FSMContext,
    user_repo: UsersRepository,
):
    await state.clear()
    user = await user_repo.get_or_create_user(callback.from_user.id)
    data = await state.get_data()
    if not data.get('user_id'):
        await state.update_data(user_id=user.id)
    if user.user_code:
        if not data.get('user_code'):
            await state.update_data(user_code=user.user_code)
        await callback.message.answer(
            "Выберите Вуз:", reply_markup=get_universities_keyboard(UNIVERSITIES)
        )
        await state.set_state(Form.waiting_for_university)
    else:
        await callback.message.answer(
            "Введите свой код, по которому можно отследить позицию в конкурсе"
        )
        await state.set_state(Form.waiting_for_code)
    await callback.answer()


@router.message(Form.waiting_for_code)
async def process_code(message: Message, state: FSMContext, user_repo: UsersRepository):
    user = await user_repo.update_user_code(message.from_user.id, message.text)
    await state.update_data(user_code=message.text)
    await message.answer(
        "Выберите Вуз:", reply_markup=get_universities_keyboard(UNIVERSITIES)
    )
    await state.set_state(Form.waiting_for_university)


@router.callback_query(F.data.startswith("uni:"))
async def process_university_selection(
    callback: CallbackQuery, state: FSMContext, univer_repo: UniversitiesRepository
):
    university = callback.data.split(":")[1]
    await state.update_data(selected_university=university)
    data = await state.get_data()
    user_id = data.get("user_id")
    if not user_id:
        await utils.get_error(callback.message, state)
        return
    directions = await univer_repo.get_user_directions_by_vuz(
        user_id=user_id, vuz_name=university
    )
    await callback.message.edit_text(
        f"Выбран Вуз: {university}",
        reply_markup=get_add_competition_keyboard(directions, university),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("add_comp:"))
async def process_add_competition(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название направления:")
    await state.set_state(Form.waiting_for_direction_name)
    await callback.answer()


@router.message(Form.waiting_for_direction_name)
async def process_directions_name(message: Message, state: FSMContext):
    await state.update_data(direction_name=message.text)
    await message.answer("Введите ссылку на интересующий вас конкурс")
    await state.set_state(Form.waiting_for_url)


@router.message(Form.waiting_for_url)
async def process_url(
    message: Message,
    state: FSMContext,
    univer_repo: UniversitiesRepository,
    user_repo: UsersRepository,
):
    await utils.update_and_respond_direction(
        event=message,
        univer_repo=univer_repo,
        user_repo=user_repo,
        state=state
    )

@router.callback_query(F.data.startswith("view_dir:"))
async def process_direction_click(callback: CallbackQuery, state: FSMContext, univer_repo: UniversitiesRepository, user_repo: UsersRepository):
    await callback.answer("Обновляю данные...")
    direction_id = int(callback.data.split(":")[1])
    
    # Вызываем ту же функцию, передав direction_id
    await utils.update_and_respond_direction(
        event=callback.message,
        univer_repo=univer_repo,
        user_repo=user_repo,
        state=state,
        direction_id=direction_id
    )