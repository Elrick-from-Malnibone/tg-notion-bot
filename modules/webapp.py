from aiogram import Router, Bot
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy import select
from core.db import get_db
from core.config import ADMIN_ID
from models.models import Note, Task
import json

router = Router()

@router.message(lambda msg: msg.web_app_data is not None)
async def handle_webapp_data(message: Message, bot: Bot):
    data = json.loads(message.web_app_data.data)
    action = data.get("action")

    if action == "get_notes":
        async for session in get_db():
            result = await session.execute(
                select(Note).where(Note.user_id == message.from_user.id).order_by(Note.created_at.desc())
            )
            notes = result.scalars().all()

        notes_data = []
        for note in notes:
            notes_data.append({
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "created_at": note.created_at.strftime("%d.%m.%Y %H:%M")
            })

        await bot.send_message(
            chat_id=message.from_user.id,
            text=json.dumps({"notes": notes_data}, ensure_ascii=False)
        )

    elif action == "create_note":
        title = data.get("title", "")
        content = data.get("content", "")

        async for session in get_db():
            note = Note(user_id=message.from_user.id, title=title, content=content)
            session.add(note)
            await session.commit()

            await bot.send_message(
                chat_id=message.from_user.id,
                text=json.dumps({"ok": True, "id": note.id}, ensure_ascii=False)
            )

    elif action == "delete_note":
        note_id = data.get("id")

        async for session in get_db():
            result = await session.execute(
                select(Note).where(Note.id == note_id, Note.user_id == message.from_user.id)
            )
            note = result.scalar_one_or_none()

            if note:
                await session.delete(note)
                await session.commit()
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text=json.dumps({"ok": True}, ensure_ascii=False)
                )

    elif action == "create_task":
        title = data.get("title", "")
        description = data.get("description", "")

        async for session in get_db():
            task = Task(user_id=message.from_user.id, title=title, description=description)
            session.add(task)
            await session.commit()

            await bot.send_message(
                chat_id=message.from_user.id,
                text=json.dumps({"ok": True, "id": task.id}, ensure_ascii=False)
            )

    elif action == "get_tasks":
        async for session in get_db():
            result = await session.execute(
                select(Task).where(Task.user_id == message.from_user.id).order_by(Task.created_at.desc())
            )
            tasks = result.scalars().all()

        tasks_data = []
        for task in tasks:
            tasks_data.append({
                "id": task.id,
                "title": task.title,
                "description": task.description or "",
                "done": task.is_done,
                "created_at": task.created_at.strftime("%d.%m.%Y %H:%M")
            })

        await bot.send_message(
            chat_id=message.from_user.id,
            text=json.dumps({"tasks": tasks_data}, ensure_ascii=False)
        )

    elif action == "delete_task":
        task_id = data.get("id")

        async for session in get_db():
            result = await session.execute(
                select(Task).where(Task.id == task_id, Task.user_id == message.from_user.id)
            )
            task = result.scalar_one_or_none()

            if task:
                await session.delete(task)
                await session.commit()
                await bot.send_message(
                    chat_id=message.from_user.id,
                    text=json.dumps({"ok": True}, ensure_ascii=False)
                )