from aiogram import Router, F
from aiogram.types import FSInputFile, Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from repository.universities import UniversitiesRepository
from states import Form
from keyboards.inline import (
    get_universities_keyboard,
    get_add_competition_keyboard,
    get_start_keyboard,
    get_profile_keyboard,
    get_custom_code_choice_keyboard,
)
from repository.users import UsersRepository
from config import BASE_DIR, UNIVERSITIES
import utils.handlers as utils

router = Router()


@router.message(Command("start"))
@router.callback_query(F.data == "back_menu")
async def command_start(event: Message | CallbackQuery):
    message: Message | None = None
    callback = False
    if isinstance(event, Message):
        message = event
    elif isinstance(event, CallbackQuery):
        message = event.message
        callback = True

    if message:
        await message.answer_photo(
            photo=FSInputFile(BASE_DIR / "icon.png"),
            caption=(
                "👋 Привет! Я *VUZOPARSER* — твой незаменимый помощник в пору поступления.\n"
                "Я избавлю тебя от бесконечного обновления сайтов приемных комиссий.\n"
                "Добавь свои направления, и я буду *автоматически отслеживать* твое место в "
                "конкурсных списках, а также пришлю уведомление, если ситуация изменится! 🔔\n"
                "✨ **Что я умею:**\n"
                "• Мониторить твою позицию 24/7.\n"
                "• Учитывать приоритеты и оригиналы.\n"
                "• Присылать моментальные уведомления.\n"
            ),
            parse_mode="Markdown",
            reply_markup=get_start_keyboard(),
        )
    if callback and isinstance(event, CallbackQuery):
        await event.answer()


@router.callback_query(F.data == "my_profile")
async def my_profile(
    callback: CallbackQuery,
    user_repo: UsersRepository,
    univer_repo: UniversitiesRepository,
    state: FSMContext,
):
    if not callback.message or not callback.from_user:
        return
    user = await user_repo.get_or_create_user(callback.from_user.id)
    if not user.user_code:
        await callback.message.answer(
            "⚠️ Вы еще не зарегистрированы. Пожалуйста, введите свой код, по которому можно отследить позицию в конкурсе:"
        )
        await state.set_state(Form.waiting_for_code)
        await callback.answer()
        return

    _, vuz_stats = await univer_repo.get_user_stats(user.id)

    stats_lines = [f" • *{vuz_name}*: {count}/5 направлений" for vuz_name, count in vuz_stats.items()]
    stats_str = "".join(stats_lines) if stats_lines else "Пока не добавлено ни одного направления."

    await callback.message.answer(
        f"👤 **Ваш профиль**\n"
        f"🔑 **Ваш код:** `{user.user_code}`\n"
        f"🏛️ **Статистика направлений:**{stats_str}\n",
        reply_markup=get_profile_keyboard(),
        parse_mode="Markdown",
    )
    await callback.answer()


@router.callback_query(F.data == "update_code")
async def update_code(callback: CallbackQuery, state: FSMContext):
    if callback.message:
        await callback.message.answer("✏️ Введите свой *новый* код для отслеживания:")
    await state.set_state(Form.updating_code)
    await callback.answer()


@router.message(Form.updating_code)
async def process_updating_code(
    message: Message,
    state: FSMContext,
    user_repo: UsersRepository,
    univer_repo: UniversitiesRepository,
):
    if not message.from_user:
        return
    await state.clear()
    user = await user_repo.update_user_code(message.from_user.id, message.text or "")
    _, vuz_stats = await univer_repo.get_user_stats(user.id)

    stats_lines = [f" • *{vuz_name}*: {count}/5 направлений" for vuz_name, count in vuz_stats.items()]
    
    stats_str = "".join(stats_lines) if stats_lines else "Пока не добавлено ни одного направления."

    await message.answer(
        f"✅ Ваш код успешно обновлен!\n"
        f"👤 **Ваш профиль**\n"
        f"🔑 **Ваш код:** `{user.user_code}`\n"
        f"🏛️ **Статистика направлений:**{stats_str}",
        reply_markup=get_profile_keyboard(),
        parse_mode="Markdown",
    )


@router.callback_query(F.data.startswith("start_registration"))
async def start_dialog(
    callback: CallbackQuery,
    state: FSMContext,
    user_repo: UsersRepository,
):
    if not callback.from_user:
        return
    await state.clear()
    user = await user_repo.get_or_create_user(callback.from_user.id)
    data = await state.get_data()
    if not data.get("user_id"):
        await state.update_data(user_id=user.id)
    if user.user_code:
        if not data.get("user_code"):
            await state.update_data(user_code=user.user_code)
        if callback.message:
            await callback.message.answer(
                "🎓 Выберите ВУЗ для отслеживания позиций:",
                reply_markup=get_universities_keyboard(UNIVERSITIES),
            )
        await state.set_state(Form.waiting_for_university)
    else:
        if callback.message:
            await callback.message.answer(
                "🔑 Введите свой *уникальный код* (СНИЛС, номер студенческого и т.п.), по которому можно отследить позицию в конкурсе:",
                parse_mode="Markdown",
            )
        await state.set_state(Form.waiting_for_code)
    await callback.answer()


@router.message(Form.waiting_for_code)
async def process_code(message: Message, state: FSMContext, user_repo: UsersRepository):
    if not message.from_user:
        return
    await user_repo.update_user_code(message.from_user.id, message.text or "")
    await state.update_data(user_code=message.text)
    await message.answer(
        "✅ Ваш код успешно сохранен! Теперь выберите ВУЗ для отслеживания позиций:",
        reply_markup=get_universities_keyboard(UNIVERSITIES),
    )
    await state.set_state(Form.waiting_for_university)


@router.callback_query(F.data.startswith("uni:"))
async def process_university_selection(
    callback: CallbackQuery, state: FSMContext, univer_repo: UniversitiesRepository
):
    if not callback.data or not callback.message or not callback.from_user:
        return
    university = callback.data.split(":")[1]
    await state.update_data(selected_university=university)
    
    user_data = await state.get_data()
    user_id = user_data.get("user_id")

    if not user_id:
        await utils.get_error(callback.message, state)
        return

    directions = await univer_repo.get_user_directions_by_vuz(user_id=user_id, vuz_name=university)
    await callback.message.edit_text(
        (f"🏛️ Вы выбрали ВУЗ: *{university}*.\n"
        f"Ваши отслеживаемые направления:"),
        reply_markup=get_add_competition_keyboard(directions, university),
        parse_mode="Markdown",
    )
    await state.set_state(Form.viewing_university)
    await callback.answer()

@router.callback_query(F.data.startswith("add_comp:"))
async def process_add_competition(callback: CallbackQuery, state: FSMContext):
    if callback.message:
        await callback.message.answer(
            "📝 Введите *название* направления, которое хотите отслеживать (например, 'Информатика'):",
            parse_mode="Markdown",
        )
    await state.set_state(Form.waiting_for_direction_name)
    await callback.answer()


@router.message(Form.waiting_for_direction_name)
async def process_directions_name(message: Message, state: FSMContext):
    await state.update_data(direction_name=message.text)
    await message.answer(
        "🔗 Отлично! Теперь отправьте *полную ссылку* на страницу конкурсного списка для этого направления:",
        parse_mode="Markdown",
    )
    await state.set_state(Form.waiting_for_url)


@router.message(Form.waiting_for_url)
async def process_url(message: Message, state: FSMContext):
    await state.update_data(url=message.text)
    await message.answer(
        "Хотите указать для этого направления отдельный код (отличный от глобального)?",
        reply_markup=get_custom_code_choice_keyboard()
    )
    await state.set_state(Form.waiting_for_custom_code_choice)

@router.callback_query(F.data == "use_custom_code", Form.waiting_for_custom_code_choice)
async def process_custom_code_choice(callback: CallbackQuery, state: FSMContext):
    if callback.message:
        await callback.message.edit_text("✏️ Введите код для этого направления:")
    await state.set_state(Form.waiting_for_custom_code)
    await callback.answer()

@router.callback_query(F.data == "use_global_code", Form.waiting_for_custom_code_choice)
async def process_global_code_choice(
    callback: CallbackQuery, state: FSMContext, univer_repo: UniversitiesRepository, user_repo: UsersRepository
):
    if callback.message:
        await utils.update_and_respond_direction(
            event=callback, univer_repo=univer_repo, user_repo=user_repo, state=state
        )
    await callback.answer()

@router.message(Form.waiting_for_custom_code)
async def process_custom_code(
    message: Message, state: FSMContext, univer_repo: UniversitiesRepository, user_repo: UsersRepository
):
    await state.update_data(custom_user_code=message.text)
    await utils.update_and_respond_direction(
        event=message, univer_repo=univer_repo, user_repo=user_repo, state=state
    )


@router.callback_query(F.data.startswith("view_dir:"))
async def process_direction_click(
    callback: CallbackQuery,
    state: FSMContext,
    univer_repo: UniversitiesRepository,
    user_repo: UsersRepository,
):
    await callback.answer("Обновляю данные...")
    if not callback.data or not callback.message:
        return
    direction_id = int(callback.data.split(":")[1])

    await utils.update_and_respond_direction(
        event=callback,
        univer_repo=univer_repo,
        user_repo=user_repo,
        state=state,
        direction_id=direction_id,
    )
