from aiogram import executor

from db.db import db_init
from handlers import dp


async def on_startup(dp):
    await db_init()


if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
