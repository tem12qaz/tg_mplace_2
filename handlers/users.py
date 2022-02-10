from aiogram import types
from aiogram.dispatcher.filters import CommandStart

from db.models import Telegram_user, Shop, Product, Photo, Deal, Review
from data.messages import *
from loader import dp, bot


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    user = await Telegram_user.get_or_none(telegram_id=message.from_user.id)
    if user is None:
        user = await Telegram_user.create(
            telegram_id=message.from_user.id, username=message.from_user.username
        )
    if user.state is None:
        await bot.send_photo(
            user.telegram_id,
            photo=open('logo.png', 'rb'),
            caption=START_MESSAGE
        )
    else:
        await message.delete()


@dp.message_handler()
async def bot_echo(message: types.Message):
    await message.answer(message.text)
