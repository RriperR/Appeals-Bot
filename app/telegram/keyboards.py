from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Описание комиссий")],
            [KeyboardButton(text="Написать обращение")],
            [KeyboardButton(text="Отследить статус")],
            [KeyboardButton(text="Помощь")],
        ],
        resize_keyboard=True,
    )


def commissions_inline(items: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=title, callback_data=f"commission:{cid}")]
        for cid, title in items
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def appeal_list_nav(has_prev: bool, has_next: bool) -> InlineKeyboardMarkup:
    row = []
    if has_prev:
        row.append(InlineKeyboardButton(text="⬅️ Предыдущие", callback_data="page:prev"))
    if has_next:
        row.append(InlineKeyboardButton(text="Следующие ➡️", callback_data="page:next"))
    return InlineKeyboardMarkup(inline_keyboard=[row] if row else [])


def skip_files_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Пропустить", callback_data="appeal:skip_files")]
        ]
    )
