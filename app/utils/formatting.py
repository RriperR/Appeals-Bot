from datetime import datetime


def format_appeal_card(
    appeal_id: int,
    commission_title: str,
    status: str,
    created_at: datetime,
    contact: str | None,
    text: str,
    files_count: int,
) -> str:
    preview = text.strip()
    if len(preview) > 140:
        preview = preview[:140] + "…"
    contact_s = contact if contact else "—"
    return (
        f"# {appeal_id} • Комиссия: «{commission_title}»\n"
        f"Статус: {status_icon(status)} {status_ru(status)}\n"
        f"Создано: {created_at:%d.%m.%Y %H:%M}\n"
        f"Контакт: {contact_s}\n"
        f"Текст: «{preview}»\n"
        f"Вложения: {files_count}"
    )


def status_icon(status: str) -> str:
    return {
        "NEW": "🟢",
        "IN_REVIEW": "🟡",
        "ON_HOLD": "🟠",
        "RESOLVED": "🟣",
        "REJECTED": "🔴",
        "DELETED": "⚫",
    }.get(status, "⚪")


def status_ru(status: str) -> str:
    return {
        "NEW": "Новое",
        "IN_REVIEW": "Рассмотрение",
        "ON_HOLD": "Пауза",
        "RESOLVED": "Завершено",
        "REJECTED": "Отклонено",
        "DELETED": "Удалено",
    }.get(status, status)
