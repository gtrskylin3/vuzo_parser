from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from format import vuz_stats
from states import Form
from sqlalchemy.ext.asyncio import AsyncSession
from keyboards.inline import get_universities_keyboard, get_add_competition_keyboard
from vuz_parser import VUZ_PARSER
from repository.users import  UsersRepository
router = Router()

UNIVERSITIES = ["НГУ", "НГТУ НЭТИ", "ТГУ"]

@router.message(Command("start"))
async def command_start(message: Message, state: FSMContext, user_repo: UsersRepository,):
    await state.clear()
    await user_repo.get_user(message.from_user.id)
    await message.answer("Введите свой код, по которому можно отследить позицию в конкурсе")
    await state.set_state(Form.waiting_for_code)

@router.message(Form.waiting_for_code)
async def process_code(message: Message, state: FSMContext, user_repo: UsersRepository):
    user = await user_repo.update_user_code(message.from_user.id, message.text)
    await state.update_data(user_code=message.text, competitions=[])
    await message.answer(
        "Выберите Вуз:",
        reply_markup=get_universities_keyboard(UNIVERSITIES)
    )
    await state.set_state(Form.waiting_for_university)

@router.callback_query(F.data.startswith("uni:"))
async def process_university_selection(callback: CallbackQuery, state: FSMContext):
    university = callback.data.split(":")[1]
    await state.update_data(selected_university=university)
    await callback.message.edit_text(
        f"Выбран Вуз: {university}",
        reply_markup=get_add_competition_keyboard(university)
    )
    await state.set_state(Form.viewing_university)
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
async def process_url(message: Message, state: FSMContext):
    user_data = await state.get_data()
    user_code = user_data.get('user_code')
    selected_university = user_data.get('selected_university')
    competition_url = message.text

    if not user_code or not selected_university:
        await message.answer("Произошла ошибка. Пожалуйста, начните сначала с /start.")
        await state.clear()
        return

    # Add the competition URL to the user's data
    competitions = user_data.get('competitions', [])
    competitions.append({'university': selected_university, 'url': competition_url})
    await state.update_data(competitions=competitions)

    await message.answer(f"Ссылка на конкурс добавлена для вуза: {selected_university}\n")

    # Attempt to parse and get data if it's NSU or NSTU
    if selected_university == 'НГУ':
        result_message = vuz_stats.format_nsu_answer(user_code, competition_url)
    elif selected_university == 'НГТУ НЭТИ':
         result_message = vuz_stats.format_nstu_answer(user_code, competition_url)

    await message.answer(result_message)
    
    # Returning to the university selection menu
    await message.answer(
        "Выберите Вуз:",
        reply_markup=get_universities_keyboard(UNIVERSITIES)
    )
    await state.set_state(Form.waiting_for_university)

