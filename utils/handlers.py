from aiogram.types import CallbackQuery, Message
from format import vuz_stats
from keyboards.inline import get_universities_keyboard, get_add_competition_keyboard
from repository.universities import UniversitiesRepository
from repository.users import UsersRepository
from aiogram.fsm.context import FSMContext
from config import UNIVERSITIES
from states import Form
from typing import cast

async def update_and_respond_direction(
    event: Message | CallbackQuery,
    univer_repo: UniversitiesRepository,
    user_repo: UsersRepository,
    state: FSMContext,
    direction_id: int | None = None
):
    target_msg: Message | None = None
    if isinstance(event, Message):
        target_msg = event
    elif isinstance(event, CallbackQuery):
        target_msg = event.message
    
    if not target_msg or not target_msg.from_user:
        return

    user_data = await state.get_data()
    user_id = user_data.get("user_id")
    
    custom_user_code = user_data.get("custom_user_code")
    user_code = custom_user_code or user_data.get("user_code")
    
    selected_university = user_data.get("selected_university")
    
    direction_name: str | None = None
    direction_url: str | None = None

    if direction_id:
        direction_obj = await univer_repo.get_direction_by_id(direction_id)
        if not direction_obj:
            await target_msg.answer("❌ Ошибка: направление не найдено в базе.")
            return
        direction_name = direction_obj.name
        direction_url = direction_obj.url
        user_direction = await user_repo.get_user_direction(user_id, direction_id)
        user_code = (user_direction and user_direction.user_code) or user_data.get("user_code")
    
    elif isinstance(event, Message):
        direction_name = user_data.get("direction_name")
        direction_url = user_data.get("url")

    if not all([user_id, user_code, selected_university, direction_name, direction_url]):
        await get_error(target_msg, state)
        return

    vuz = await univer_repo.get_or_create_vuz(selected_university)

    if custom_user_code:
        await user_repo.update_user_codes_for_vuz(user_id, vuz.id, int(custom_user_code))
        await state.update_data(custom_user_code=None)

    result_message = ""
    position = None

    if selected_university == "НГУ":
        result_message, position = vuz_stats.format_nsu_answer(user_code, direction_url)
    elif selected_university == "НГТУ НЭТИ":
        result_message, position = vuz_stats.format_nstu_answer(user_code, direction_url)
    elif selected_university == "ТГУ":
        result_message, position = vuz_stats.format_tgu_answer(user_code, direction_url)
    elif selected_university == "ТПУ":
        result_message, position = vuz_stats.format_tpu_answer(user_code, direction_url)
    else:
        await get_error(target_msg, state)
        return

    await target_msg.answer(result_message)
    if not position:
        await get_error(target_msg, state)
        return

    direction = await univer_repo.get_or_create_direction(
        vuz_id=vuz.id,
        direction_name=cast(str, direction_name),
        direction_url=cast(str, direction_url),
    )

    is_linked, old_position = await user_repo.add_direction(
        user_id=cast(int, user_id),
        direction_id=direction.id,
        position=int(position),
        user_code=int(custom_user_code) if custom_user_code else None
    )

    if not is_linked:
        await target_msg.answer("❌ Вы не можете добавить более 5 направлений для одного ВУЗа!")
        return

    if old_position and (int(position) != old_position):
        await target_msg.answer(
            f"""🔥 Ваша позиция в конкурсе **{direction_name}** изменилась!
Было: {old_position}
Стало: {position}""", 
            parse_mode="Markdown"
        )
    
    directions = await univer_repo.get_user_directions_by_vuz(user_id=cast(int, user_id), vuz_name=selected_university)
    await target_msg.answer(
        f"✅ Направление обновлено! Ваши отслеживаемые направления в *{selected_university}*:",
        reply_markup=get_add_competition_keyboard(directions, selected_university),
        parse_mode="Markdown"
    )
    await state.set_state(Form.viewing_university)


async def get_error(message: Message, state: FSMContext | None):
    await message.answer("Произошла ошибка. Пожалуйста, начните сначала с /start.")
    if state:
        await state.clear()
