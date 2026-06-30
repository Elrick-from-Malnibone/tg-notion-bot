from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from sqlalchemy import select, func
from datetime import datetime, timedelta
from core.config import ADMIN_ID
from core.db import get_db
from models.models import User, UserEvent, Note, Task

router = Router()

async def register_user(user_id: int, username: str | None):
    async for session in get_db():
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if user is None:
            user = User(id=user_id, username=username)
            session.add(user)

            event = UserEvent(user_id=user_id, event="registered")
            session.add(event)

            await session.commit()
            return True  # новый юзер
        return False  # уже был


@router.message(CommandStart())
async def cmd_start(message: Message):
    is_new = await register_user(message.from_user.id, message.from_user.username)

    if is_new:
            await message.bot.send_message(
                ADMIN_ID,
                f"Новый пользователь: @{message.from_user.username or 'без юзернейма'} ({message.from_user.id})"
            )

    await message.answer("Добро пожаловать в TG Notion!")


@router.message(Command("active"))
async def cmd_active(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    async for session in get_db():
        # Юзеры с заметками
        notes_result = await session.execute(
            select(Note.user_id).distinct()
        )
        notes_users = set(row[0] for row in notes_result)

        # Юзеры с задачами
        tasks_result = await session.execute(
            select(Task.user_id).distinct()
        )
        tasks_users = set(row[0] for row in tasks_result)

        active_users = notes_users | tasks_users
        total = await session.scalar(select(func.count(User.id)))

    await message.answer(
        f"📊 Активность:\n"
        f"- Всего юзеров: {total}\n"
        f"- Создали заметок/задач: {len(active_users)}\n"
        f"- Просто зашли: {total - len(active_users)}"
    )

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    async for session in get_db():
        # Всего юзеров
        total_users = await session.scalar(select(func.count(User.id)))

        # За сегодня
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        new_today = await session.scalar(
            select(func.count(User.id)).where(User.created_at >= today)
        )

        # За неделю
        week_ago = today - timedelta(days=7)
        new_week = await session.scalar(
            select(func.count(User.id)).where(User.created_at >= week_ago)
        )

        # Заметок и задач
        total_notes = await session.scalar(select(func.count(Note.id)))
        total_tasks = await session.scalar(select(func.count(Task.id)))

        # Последние 5
        last_users = await session.execute(
            select(User.username, User.created_at)
            .order_by(User.created_at.desc())
            .limit(5)
        )
        last = last_users.all()

    last_text = "\n".join(
        f"@{u[0] or 'без'} — {u[1].strftime('%d.%m.%Y %H:%M')}" for u in last
    ) or "никого"

    await message.answer(
        f"Юзеры:\n"
        f"- Всего: {total_users}\n"
        f"- За сегодня: {new_today}\n"
        f"- За неделю: {new_week}\n\n"
        f"Контент:\n"
        f"- Заметок: {total_notes}\n"
        f"- Задач: {total_tasks}\n\n"
        f"Последние 5:\n{last_text}"
    )

@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, bot: Bot):
    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.split(maxsplit=1)
    if len(text) < 2:
        await message.answer("Использование: /broadcast Текст рассылки")
        return

    async for session in get_db():
        result = await session.execute(select(User.id))
        users = result.scalars().all()

    success = 0
    fail = 0
    for user_id in users:
        try:
            await bot.send_message(user_id, text[1])
            success += 1
        except:
            fail += 1

    await message.answer(f"Рассылка завершена:\n- Отправлено: {success}\n- Не доставлено: {fail}")    