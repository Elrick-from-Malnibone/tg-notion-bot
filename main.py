import asyncio
from aiogram import Bot, Dispatcher
from core.config import BOT_TOKEN
from core.db import init_db
from core.router import setup_routers

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def main():
    await init_db()
    setup_routers(dp)
    print("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())