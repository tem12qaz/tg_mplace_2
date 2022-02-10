from aiogram import types
from aiogram.dispatcher.filters import CommandStart

from data.config import FLOOD_RATE, ADMIN_ID
from db.models import TelegramUser, Shop, Product, Photo, Deal, Review
from data.messages import *
from keyboards.inline.keyboards import start_keyboard, start_callback, back_to_main_menu_keyboard, support_keyboard, \
    get_admin_answer_keyboard, admin_callback
from loader import dp, bot


@dp.message_handler(CommandStart())
@dp.throttled(rate=FLOOD_RATE)
async def bot_start(message: types.Message):
    user = await TelegramUser.get_or_none(telegram_id=message.from_user.id)
    if user is None:
        user = await TelegramUser.create(
            telegram_id=message.from_user.id, username=message.from_user.username
        )
        await bot.send_photo(
            user.telegram_id,
            photo=open('logo.png', 'rb'),
            caption=START_MESSAGE,
            reply_markup=start_keyboard
        )
        return

    if user.state is None:
        await message.answer(
            MAIN_MENU_MESSAGE,
            reply_markup=start_keyboard
        )
    else:
        await message.delete()


@dp.callback_query_handler(start_callback.filter())
@dp.throttled(rate=FLOOD_RATE)
async def main_menu(callback: types.CallbackQuery, callback_data):
    await callback.answer()
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)
    if user is None:
        return

    select = callback_data.get('select')

    if select == 'shops':
        pass

    elif select == 'seller':
        pass

    elif select == 'about':
        await bot.send_photo(
            user.telegram_id,
            photo=open('logo.png', 'rb'),
        )
        await bot.send_message(
            user.telegram_id,
            ABOUT_US_MESSAGE,
            reply_markup=back_to_main_menu_keyboard
        )

    elif select == 'support':
        await bot.send_photo(
            user.telegram_id,
            photo=open('logo.png', 'rb'),
        )
        await bot.send_message(
            user.telegram_id,
            SUPPORT_MESSAGE,
            reply_markup=support_keyboard
        )

    elif select == 'main':
        user.state = None
        await user.save()
        await bot.edit_message_text(
            MAIN_MENU_MESSAGE,
            user.telegram_id,
            callback.message.message_id,
            reply_markup=start_keyboard
        )

    elif select == 'admin_message':
        user.state = 'admin_message'
        await user.save()
        await bot.edit_message_text(
            ADMIN_MESSAGE,
            user.telegram_id,
            callback.message.message_id,
            reply_markup=back_to_main_menu_keyboard
        )

    else:
        return


@dp.message_handler()
@dp.throttled(rate=FLOOD_RATE)
async def listen_handler(message: types.Message):
    user = await TelegramUser.get_or_none(telegram_id=message.from_user.id)
    if user is None:
        return

    if user.state is None:
        await message.delete()

    elif user.state == 'admin_message':
        user.state = None
        await user.save()
        await bot.send_message(
            ADMIN_ID,
            ADMIN_READ_MESSAGE.format(message=message.text),
            reply_markup=get_admin_answer_keyboard(user)
        )
        await message.answer(
            ADMIN_SENT_MESSAGE,
            reply_markup=back_to_main_menu_keyboard
        )

    elif 'admin_answer' in user.state:
        state = user.state
        user.state = None
        await user.save()
        if int(user.telegram_id) != ADMIN_ID:
            return

        tg_id = state.split('_')[2]
        await bot.send_message(
            tg_id,
            ADMIN_ANSWER_MESSAGE.format(answer=message.text)
        )
        await message.answer(
            ADMIN_SENT_MESSAGE
        )


@dp.callback_query_handler(admin_callback.filter())
@dp.throttled(rate=FLOOD_RATE)
async def main_menu(callback: types.CallbackQuery, callback_data):
    await callback.answer()
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)

    if user is None:
        return
    elif int(user.telegram_id) != ADMIN_ID:
        return

    action = callback_data.get('action')
    param = callback_data.get('param')

    if action == 'answer':
        user.state = 'admin_answer_' + param
        await user.save()
        await bot.send_message(
            callback.from_user.id,
            ADMIN_WRITE_MESSAGE
        )
