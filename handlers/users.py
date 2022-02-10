import os

from aiogram import types
from aiogram.dispatcher.filters import CommandStart

from data.config import FLOOD_RATE, ADMIN_ID
from db.models import TelegramUser, Shop, Product, Photo, Deal, Review, Category
from data.messages import *
from keyboards.inline.keyboards import start_callback, back_to_main_menu_keyboard, support_keyboard, \
    get_admin_answer_keyboard, admin_callback, get_start_keyboard, get_seller_keyboard, seller_callback, \
    create_type_shop_keyboard, get_seller_categories_keyboard, seller_main_menu_keyboard, get_admin_shop_keyboard
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
            reply_markup=await get_start_keyboard(user)
        )
        return

    await check_creating_shop(user)

    await message.answer(
        MAIN_MENU_MESSAGE,
        reply_markup=await get_start_keyboard(user)
    )


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

    elif select == 'services':
        pass

    elif select == 'seller':
        await bot.edit_message_text(
            MENU_MESSAGE,
            user.telegram_id,
            callback.message.message_id,
            reply_markup=await get_seller_keyboard(user)
        )

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
        user.state = ''
        await user.save()
        await bot.edit_message_text(
            MAIN_MENU_MESSAGE,
            user.telegram_id,
            callback.message.message_id,
            reply_markup=await get_start_keyboard(user)
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
        user.state = ''
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
        user.state = ''
        await user.save()
        if int(user.telegram_id) != ADMIN_ID:
            return

        tg_id = state.split('_')[-1]
        await bot.send_message(
            tg_id,
            ADMIN_ANSWER_MESSAGE.format(answer=message.text)
        )
        await message.answer(
            ADMIN_SENT_MESSAGE
        )

    elif 'listen_shop_name_' in user.state:
        shop = await Shop.get_or_none(id=int(user.state.replace('listen_shop_name_', '')))
        if shop is None:
            return
        shop.name = message.text
        await shop.save()
        user.state = 'listen_shop_description_' + str(shop.id)
        await user.save()
        await message.answer(
            INPUT_SHOP_DESCRIPTION_MESSAGE,
            reply_markup=seller_main_menu_keyboard
        )

    elif 'listen_shop_description_' in user.state:
        shop = await Shop.get_or_none(id=int(user.state.replace('listen_shop_description_', '')))
        if shop is None:
            return
        shop.description = message.text
        await shop.save()
        user.state = 'listen_shop_photo_' + str(shop.id)
        await user.save()
        await message.answer(
            INPUT_SHOP_PHOTO_MESSAGE,
            reply_markup=seller_main_menu_keyboard
        )


@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    user = await TelegramUser.get_or_none(telegram_id=message.chat.id)
    if user is None:
        return

    if 'listen_shop_photo_' in user.state:
        shop = await Shop.get_or_none(id=int(user.state.replace('listen_shop_photo_', '')))
        if shop is None:
            return

        photo = message.photo[-1]
        name = f'files/{message.from_user.id}_{photo.file_id}.jpg'
        await photo.download(destination_file=name)

        photo_binary = open(name, 'rb').read()
        shop.photo = photo_binary
        await shop.save()
        os.remove(name)

        user.state = ''
        await user.save()

        await message.answer(
            SHOP_CREATED_MESSAGE,
            reply_markup=seller_main_menu_keyboard
        )

        await bot.send_photo(
            ADMIN_ID,
            photo=photo_binary,
            caption=ADMIN_CREATE_SHOP_MESSAGE.format(
                name=shop.name, description=shop.description
            ),
            reply_markup=get_admin_shop_keyboard(shop)
        )


@dp.callback_query_handler(admin_callback.filter())
@dp.throttled(rate=FLOOD_RATE)
async def admin_handler(callback: types.CallbackQuery, callback_data):
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

    elif action == 'apply':
        shop = await Shop.get_or_none(id=int(param))
        if shop is None:
            return
        shop.active = True
        await shop.save()
        await bot.delete_message(ADMIN_ID, callback.message.message_id)

        await bot.send_message(
            (await shop.owner).telegram_id,
            SHOP_ACTIVATED_MESSAGE.format(name=shop.name)
        )

    elif action == 'decline':
        shop = await Shop.get_or_none(id=int(param))
        if shop is None:
            return
        await shop.delete()
        await shop.save()
        await bot.delete_message(ADMIN_ID, callback.message.message_id)

        await bot.send_message(
            (await shop.owner).telegram_id,
            SHOP_DECLINED_MESSAGE.format(name=shop.name)
        )


@dp.callback_query_handler(seller_callback.filter())
@dp.throttled(rate=FLOOD_RATE)
async def seller_handler(callback: types.CallbackQuery, callback_data):
    await callback.answer()
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)

    if user is None:
        return

    action = callback_data.get('action')
    shop = callback_data.get('shop')

    if action == 'open_shop':
        await bot.edit_message_text(
            CREATE_SHOP_TYPE_MESSAGE,
            user.telegram_id,
            callback.message.message_id,
            reply_markup=create_type_shop_keyboard
        )

    elif action == 'create_catalog' or action == 'create_bid':
        shop = await Shop.create(
            owner=user,
            name='',
            description='',
            catalog=True if action == 'create_catalog' else False
        )
        user.state = 'create_shop_' + str(shop.id)
        await user.save()
        await bot.edit_message_text(
            CREATE_SHOP_CATEGORY_MESSAGE,
            user.telegram_id,
            callback.message.message_id,
            reply_markup=await get_seller_categories_keyboard(shop.id)
        )

    elif 'select_cat_' in action:
        category = await Category.get_or_none(id=int(action.split('_')[-1]))
        shop = await Shop.get_or_none(id=int(shop))
        if category is None or shop is None:
            return
        shop.category = category
        await shop.save()

        user.state = 'listen_shop_name_' + str(shop.id)
        await user.save()

        await bot.edit_message_text(
            INPUT_SHOP_NAME_MESSAGE,
            user.telegram_id,
            callback.message.message_id,
            reply_markup=seller_main_menu_keyboard
        )

    elif action == 'main':
        await check_creating_shop(user)
        await bot.edit_message_text(
            MENU_MESSAGE,
            user.telegram_id,
            callback.message.message_id,
            reply_markup=await get_seller_keyboard(user)
        )


async def check_creating_shop(user):
    if 'create_shop_' in user.state or \
            'listen_shop_name_' in user.state or \
            'listen_shop_description_' in user.state or \
            'listen_shop_photo_' in user.state:
        shop = await user.shops.filter(id=int(user.state.split('_')[-1]))
        await shop[0].delete()
        user.state = ''
        await user.save()
