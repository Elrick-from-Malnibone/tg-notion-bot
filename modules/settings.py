from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select
from core.db import get_db
from models.models import User

router = Router()

@router.message(Command("theme"))
async def cmd_theme(message: Message):
    async for session in get_db():
        result = await session.execute(select(User).where(User.id == message.from_user.id))
        user = result.scalar_one_or_none()

        if user is None:
            await message.answer("Сначала напишите /start")
            return

        if user.theme == "dark":
            user.theme = "light"
            await session.commit()
            await message.answer("☀️ Тема переключена на светлую")
        else:
            user.theme = "dark"
            await session.commit()
            await message.answer("🌙 Тема переключена на тёмную")