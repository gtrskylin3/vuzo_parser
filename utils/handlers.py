from aiogram.types import CallbackQuery, Message
from format import vuz_stats
from keyboards.inline import get_universities_keyboard
from repository.universities import UniversitiesRepository
from repository.users import UsersRepository
from aiogram.fsm.context import FSMContext
from config import UNIVERSITIES
from states import Form

async def update_and_respond_direction(
    event: Message | CallbackQuery, # Теперь может принимать CallbackQuery, как и command_start
    univer_repo: UniversitiesRepository,
    user_repo: UsersRepository,
    state: FSMContext,
    direction_id: int | None = None  # Передаем только если кликнули по кнопке направления
):
    # Автоматически определяем, куда слать сообщения
    target_msg = event if isinstance(event, Message) else event.message
    if not target_msg:
        return
    # 1. Извлекаем ВСЕ базовые данные из стейта за один раз
    user_data = await state.get_data()
    user_id = user_data.get("user_id")
    user_code = user_data.get("user_code")
    selected_university = user_data.get("selected_university")
    
    # 2. Определяем имя направления и URL в зависимости от того, как вызвана функция
    if direction_id:
        # Если пришли из кнопки: берем всё из БД по ID направления
        direction_obj = await univer_repo.get_direction_by_id(direction_id)
        if not direction_obj:
            await target_msg.answer("❌ Ошибка: направление не найдено в базе.")
            return
        direction_name = direction_obj.name
        direction_url = direction_obj.url
    else:
        # Если пришли из текстового ввода: берем название из стейта, а ссылку из сообщения
        direction_name = user_data.get("direction_name")
        direction_url = event.text  # так как event — это Message

    # Валидация данных
    if not all([user_id, user_code, selected_university, direction_name, direction_url]):
        await get_error(target_msg, state)
        return

    # 3. Запуск парсера
    if selected_university == "НГУ":
        result_message, budget, position = vuz_stats.format_nsu_answer(user_code, direction_url)
    elif selected_university == "НГТУ НЭТИ":
        result_message, budget, position = vuz_stats.format_nstu_answer(user_code, direction_url)
    elif selected_university == "ТГУ":
        result_message, budget, position = vuz_stats.format_tgu_answer(user_code, direction_url)
    elif selected_university == "ТПУ":
        result_message, budget, position = vuz_stats.format_tpu_answer(user_code, direction_url)
    else:
        await get_error(target_msg, state)
        return

    await target_msg.answer(result_message)
    if not position:
        await get_error(target_msg, state)
        return

    # 4. Работа с базой данных
    vuz = await univer_repo.get_or_create_vuz(selected_university)

    # Шаг 1: Получаем или создаем общее, не привязанное к юзеру направление
    direction = await univer_repo.get_or_create_direction(
        vuz_id=vuz.id,
        direction_name=direction_name,
        direction_url=direction_url,
    )

    # Шаг 2: Привязываем направление к пользователю и обновляем его позицию
    is_linked, old_position = await user_repo.add_direction(
        user_id=user_id,
        direction_id=direction.id,
        position=int(position)  # Передаем позицию из парсера!
    )

    if not is_linked:
        await target_msg.answer("❌ Вы не можете добавить более 5 направлений!")
        return

    if old_position and (int(position) != old_position):
        await target_msg.answer(
            (f"🔥 Ваша позиция в конкурсе **{direction_name}** изменилась!\n"
             f"Было: {old_position}\n"
             f"Стало: {position}"), 
             parse_mode="Markdown"
        )
    if not old_position:
        await target_msg.answer(
            "✅ Направление *добавлено* в отслеживание! Выберите ВУЗ:", parse_mode="Markdown", reply_markup=get_universities_keyboard(UNIVERSITIES)
        )
    else:
        await target_msg.answer(
            "🎓 Выберите ВУЗ:", parse_mode="Markdown", reply_markup=get_universities_keyboard(UNIVERSITIES)
        )
    await state.set_state(Form.waiting_for_university)


async def get_error(message: Message, state: FSMContext | None):
    await message.answer("Произошла ошибка. Пожалуйста, начните сначала с /start.")
    if state:
        await state.clear()
