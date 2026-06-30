from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select
from core.db import get_db
from models.models import Note
import json

router = Router()

@router.message(Command("notes"))
async def cmd_notes_list(message: Message):
    async for session in get_db():
        result = await session.execute(
            select(Note).where(Note.user_id == message.from_user.id).order_by(Note.created_at.desc())
        )
        notes = result.scalars().all()

    if not notes:
        await message.answer("У вас пока нет заметок")
        return

    text = "📝 Ваши заметки:\n\n"
    for note in notes:
        text += f"/note_{note.id} — {note.title}\n"

    await message.answer(text)


@router.message(Command("note_create"))
async def cmd_note_create(message: Message):
    # Формат: /note_create Заголовок | Содержимое
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Использование: /note_create Заголовок | Содержимое")
        return

    parts = args[1].split("|", maxsplit=1)
    title = parts[0].strip()
    content = parts[1].strip() if len(parts) > 1 else ""

    async for session in get_db():
        note = Note(user_id=message.from_user.id, title=title, content=content)
        session.add(note)
        await session.commit()
        await message.answer(f"✅ Заметка создана: {title}")


@router.message(Command("note_delete"))
async def cmd_note_delete(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: /note_delete ID")
        return

    note_id = args[1]

    async for session in get_db():
        result = await session.execute(
            select(Note).where(Note.id == int(note_id), Note.user_id == message.from_user.id)
        )
        note = result.scalar_one_or_none()

        if note is None:
            await message.answer("Заметка не найдена")
            return

        await session.delete(note)
        await session.commit()
        await message.answer(f"🗑 Заметка удалена")

@router.message(Command("get_notes"))
async def cmd_get_notes_json(message: Message):
    async for session in get_db():
        result = await session.execute(
            select(Note).where(Note.user_id == message.from_user.id).order_by(Note.created_at.desc())
        )
        notes = result.scalars().all()

    data = []
    for note in notes:
        data.append({
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "created_at": note.created_at.strftime("%d.%m.%Y %H:%M")
        })

    await message.answer(json.dumps(data, ensure_ascii=False, indent=2))        