from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError

from app.telegram.states.commission import CommissionAddFSM
from app.core.settings import settings
from app.db.session import async_session
from app.db.repositories import CommissionRepo


router = Router()


def is_admin(uid: int) -> bool:
    return uid in set(settings.admin_ids or [])


@router.callback_query(F.data == "admin:commissions:add")
async def commissions_add_entry(c: types.CallbackQuery, state: FSMContext):
    if not is_admin(c.from_user.id):
        await c.answer("Нет прав", show_alert=True); return
    await state.set_state(CommissionAddFSM.ask_title)
    await c.message.edit_text("➕ Введите название комиссии:")


@router.message(CommissionAddFSM.ask_title, F.text)
async def commissions_add_title(m: types.Message, state: FSMContext):
    title = m.text.strip()
    if len(title) < 3:
        await m.answer("Название слишком короткое, минимум 3 символа. Повторите:")
        return
    await state.update_data(title=title)
    await state.set_state(CommissionAddFSM.ask_description)
    await m.answer("Введите описание комиссии (или «-» чтобы оставить пустым):")


@router.message(CommissionAddFSM.ask_description, F.text)
async def commissions_add_desc(m: types.Message, state: FSMContext):
    data = await state.get_data()
    title = data["title"]
    desc = None if m.text.strip() == "-" else m.text.strip()

    async with async_session() as session:
        exists = await CommissionRepo.by_title(session, title)
        if exists:
            await m.answer("Комиссия с таким названием уже существует.")
            await state.clear()
            return
        try:
            obj = await CommissionRepo.create(session, title, desc)
            await session.commit()
        except IntegrityError:
            await session.rollback()
            await m.answer("Ошибка сохранения (возможно, дубликат). Попробуйте снова.")
            await state.clear()
            return

    await state.clear()
    await m.answer(f"✅ Комиссия «{obj.title}» создана (id={obj.id}).")


@router.callback_query(F.data == "admin:commissions:list")
async def commissions_list(c: types.CallbackQuery):
    if not is_admin(c.from_user.id):
        await c.answer("Нет прав", show_alert=True); return
    async with async_session() as session:
        items = await CommissionRepo.list_active(session)
    if not items:
        await c.message.edit_text("Активных комиссий нет.")
        return
    text = "📋 Активные комиссии:\n" + "\n".join(f"• [{x.id}] {x.title}" for x in items)
    await c.message.edit_text(text)
