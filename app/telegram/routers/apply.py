from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from sqlalchemy import select

from app.telegram.states.appeal import AppealFSM
from app.telegram.keyboards import commissions_inline
from app.db.session import async_session
from app.db.repositories import UserRepo, AppealRepo


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
    await state.update_data(commission_id=cid, files=[])
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
    await m.answer("Хотите прикрепить файл? Отправляйте фото/документы. Когда закончите — напишите «Пропустить».")

@router.message(AppealFSM.ask_file, F.text.lower() == "пропустить")
async def files_done(m: types.Message, state: FSMContext):
    data = await state.get_data()
    files: list[tuple[str, str | None, str | None]] = data.get("files", [])
    commission_id: int = data["commission_id"]
    contact: str | None = data.get("contact")
    text: str = data["text"]

    async with async_session() as session:
        user = await UserRepo.upsert_from_telegram(
            session,
            tg_id=m.from_user.id,
            full_name=m.from_user.full_name,
            username=m.from_user.username,
        )
        appeal = await AppealRepo.create(
            session,
            user_id=user.id,
            commission_id=commission_id,
            text=text,
            contact=contact,
            files=files,
        )
        await session.commit()

    await state.clear()
    await m.answer(f"✅ Ваше обращение отправлено! Номер: #{appeal.id}")

@router.message(AppealFSM.ask_file, F.document)
async def on_document(m: types.Message, state: FSMContext):
    d = m.document
    file_tuple = (d.file_id, d.file_name, d.mime_type)
    data = await state.get_data()
    files = data.get("files", [])
    files.append(file_tuple)
    await state.update_data(files=files)
    await m.answer(f"📎 Документ добавлен: {d.file_name or 'файл'}.\n"
                   f"Отправьте ещё файл или напишите «Пропустить».")

@router.message(AppealFSM.ask_file, F.photo)
async def on_photo(m: types.Message, state: FSMContext):
    p = m.photo[-1]  # максимальное качество
    file_tuple = (p.file_id, None, "image/jpeg")
    data = await state.get_data()
    files = data.get("files", [])
    files.append(file_tuple)
    await state.update_data(files=files)
    await m.answer("Фото добавлено. Ещё файл — или «Пропустить».")
