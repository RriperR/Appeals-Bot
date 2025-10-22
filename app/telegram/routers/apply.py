from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy import select

from app.telegram.states.appeal import AppealFSM
from app.telegram.keyboards import commissions_inline
from app.db.session import async_session


router = Router()

@router.message(F.text == "Написать обращение")
async def apply_start(m: types.Message, state: FSMContext):
    async with async_session() as session:
        rows = (await session.execute(
            select(m.Commission.id, m.Commission.title).where(m.Commission.is_active == True)  # noqa
        )).all()
        if not rows:
            await m.answer("Пока нет доступных комиссий. Попробуйте позже.")
            return
        kb = commissions_inline([(r[0], r[1]) for r in rows])
    await state.set_state(AppealFSM.choose_commission)
    await m.answer("📝 Выберите комиссию:", reply_markup=ReplyKeyboardRemove())
    await m.answer("Список комиссий:", reply_markup=kb)

@router.callback_query(AppealFSM.choose_commission, F.data.startswith("commission:"))
async def choose_commission(c: types.CallbackQuery, state: FSMContext):
    cid = int(c.data.split(":")[1])
    await state.update_data(commission_id=cid)
    await state.set_state(AppealFSM.ask_contact)
    await c.message.edit_text("📲 Введите телефон или email (или «-» для анонимного обращения).")

@router.message(AppealFSM.ask_contact)
async def save_contact(m: types.Message, state: FSMContext):
    contact = None if m.text.strip() == "-" else m.text.strip()
    await state.update_data(contact=contact)
    await state.set_state(AppealFSM.ask_text)
    await m.answer("✍️ Напишите ваше обращение (не менее 20 символов):")

@router.message(AppealFSM.ask_text, F.text.len() >= 20)
async def receive_text(m: types.Message, state: FSMContext):
    await state.update_data(text=m.text.strip())
    await state.set_state(AppealFSM.ask_file)
    await m.answer("Хотите прикрепить файл? Отправьте фото/документ или напишите «Пропустить».")
