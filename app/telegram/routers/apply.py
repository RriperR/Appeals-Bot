from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from sqlalchemy import select

from app.telegram.states.appeal import AppealFSM
from app.telegram.keyboards import commissions_inline, skip_files_inline
from app.db.session import async_session
from app.db.repositories import UserRepo, AppealRepo
from app.db.models import Commission


router = Router()


@router.message(F.text == "Написать обращение")
async def apply_start(msg: Message, state: FSMContext):
    async with async_session() as session:
        rows = (await session.execute(
            select(Commission.id, Commission.title).where(Commission.is_active == True)  # noqa
        )).all()
    if not rows:
        await msg.answer("Пока нет доступных комиссий. Попробуйте позже.")
        return
    kb = commissions_inline([(r[0], r[1]) for r in rows])
    await state.set_state(AppealFSM.choose_commission)
    await msg.answer("📝 Выберите комиссию:", reply_markup=ReplyKeyboardRemove())
    await msg.answer("Список комиссий:", reply_markup=kb)


@router.callback_query(AppealFSM.choose_commission, F.data.startswith("commission:"))
async def choose_commission(clbk: CallbackQuery, state: FSMContext):
    cid = int(clbk.data.split(":")[1])
    await state.update_data(commission_id=cid, files=[])
    await state.set_state(AppealFSM.ask_contact)
    await clbk.message.edit_text("📲 Введите телефон или email (или «-» для анонимного обращения).")


@router.message(AppealFSM.ask_contact)
async def save_contact(msg: Message, state: FSMContext):
    contact = None if msg.text.strip() == "-" else msg.text.strip()
    await state.update_data(contact=contact)
    await state.set_state(AppealFSM.ask_text)
    await msg.answer("✍️ Напишите ваше обращение (не менее 20 символов):")


@router.message(AppealFSM.ask_text, F.text.len() >= 20)
async def receive_text(msg: Message, state: FSMContext):
    await state.update_data(text=msg.text.strip())
    await state.set_state(AppealFSM.ask_file)
    await msg.answer(
        "Хотите прикрепить файл? Отправляйте фото/документы. Когда закончите — нажмите «Пропустить».",
        reply_markup=skip_files_inline(),  # <<< добавили кнопку
    )


@router.callback_query(AppealFSM.ask_file, F.data == "appeal:skip_files")
async def files_done_cb(clbk: CallbackQuery, state: FSMContext):
    # переиспользуем логику сохранения обращения
    class DummyMessage:
        def __init__(self, from_user, chat, answer):
            self.from_user = from_user
            self.chat = chat
            self.answer = answer
    # аккуратно: лучше вынести в отдельную функцию, но для краткости — дернём общий код:
    await files_done(clbk.message, state)


@router.message(AppealFSM.ask_file, F.text.lower() == "пропустить")
async def files_done(msg: Message, state: FSMContext):
    data = await state.get_data()
    files: list[tuple[str, str | None, str | None]] = data.get("files", [])
    commission_id: int = data["commission_id"]
    contact: str | None = data.get("contact")
    text: str = data["text"]

    async with async_session() as session:
        user = await UserRepo.upsert_from_telegram(
            session,
            tg_id=msg.from_user.id,
            full_name=msg.from_user.full_name,
            username=msg.from_user.username,
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
    await msg.answer(f"✅ Ваше обращение отправлено! Номер: #{appeal.id}")


@router.message(AppealFSM.ask_file, F.document)
async def on_document(msg: Message, state: FSMContext):
    d = msg.document
    file_tuple = (d.file_id, d.file_name, d.mime_type)
    data = await state.get_data()
    files = data.get("files", [])
    files.append(file_tuple)
    await state.update_data(files=files)
    await msg.answer(f"📎 Документ добавлен: {d.file_name or 'файл'}.\n"
                   f"Отправьте ещё файл или напишите «Пропустить».")


@router.message(AppealFSM.ask_file, F.photo)
async def on_photo(msg: Message, state: FSMContext):
    p = msg.photo[-1]  # максимальное качество
    file_tuple = (p.file_id, None, "image/jpeg")
    data = await state.get_data()
    files = data.get("files", [])
    files.append(file_tuple)
    await state.update_data(files=files)
    await msg.answer("Фото добавлено. Ещё файл — или «Пропустить».")
