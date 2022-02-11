import os

from aiogram import types
from aiogram.dispatcher.filters import CommandStart, CommandHelp
from aiogram.types import InputMediaPhoto
from parse import parse

from data.config import FLOOD_RATE, ADMIN_ID
from db.models import TelegramUser, Shop, Product, Photo, Deal, Review, Category, CategoryShop
from data.messages import *
from keyboards.inline.keyboards import start_callback, back_to_main_menu_keyboard, support_keyboard, \
    get_admin_answer_keyboard, admin_callback, get_start_keyboard, get_seller_keyboard, seller_callback, \
    create_type_shop_keyboard, get_seller_categories_keyboard, seller_main_menu_keyboard, get_admin_shop_keyboard, \
    get_seller_shop_info_keyboard, get_go_seller_shop_info_keyboard, get_admin_edit_shop_keyboard, \
    get_seller_shop_delete_keyboard, get_seller_shop_categories_keyboard, get_go_seller_categories_keyboard, \
    get_seller_category_keyboard, get_go_seller_category_keyboard, get_seller_delete_category_keyboard, \
    get_seller_products_keyboard, get_go_seller_products_keyboard, get_go_seller_product_keyboard, \
    get_seller_product_info_keyboard, get_seller_add_photo_product_keyboard, get_delete_product_keyboard
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

    await check_creating(user)

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
    message_ = message
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
        shop.name = message.text[:100]
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

    elif 'change_shop_' in user.state:
        shop_id, field = user.state.replace('change_shop_', '').split('_')
        if shop_id == 'photo':
            return
        shop = await Shop.get_or_none(id=int(shop_id))
        if shop is None:
            return
        if field == 'name':
            message = ADMIN_EDIT_SHOP_NAME_MESSAGE.format(
                name=message.text, old_name=shop.name
            )
        elif field == 'description':
            message = ADMIN_EDIT_SHOP_DESCRIPTION_MESSAGE.format(
                description=message.text, old_description=shop.description
            )
        else:
            return

        await bot.send_message(
            ADMIN_ID,
            message,
            reply_markup=get_admin_edit_shop_keyboard(shop, field)
        )
        await message_.answer(
            SHOP_CREATED_MESSAGE,
            reply_markup=get_go_seller_shop_info_keyboard(shop)
        )

    elif 'listen_category_name_' in user.state:
        shop_id, category_id = user.state.replace('listen_category_name_', '').split('_')
        shop = await Shop.get_or_none(id=int(shop_id))
        if shop is None:
            return

        if category_id == '':
            await CategoryShop.create(name=message.text[:100], shop=shop)

        else:
            category = await CategoryShop.get_or_none(id=int(category_id))
            if category is None:
                return
            category.name = message.text
            await category.save()

        await message.answer(
            SAVED_MESSAGE,
            reply_markup=get_go_seller_categories_keyboard(shop)
        )
    elif 'listen_product_' in user.state:
        edit = False
        if 'edit' in user.state:
            user.state = user.state.replace('edit', '')
            edit = True

        field, product_id = user.state.replace('listen_product_', '').split('_')
        product = await Product.get_or_none(id=product_id)

        if product is None:
            return

        category = await product.category
        shop = await category.shop
        keyboard = get_go_seller_products_keyboard(shop, category)

        if field == 'name':
            user.state = 'listen_product_description_' + str(product_id)
            product.name = message.text
            message = ADD_PRODUCT_DESCRIPTION_MESSAGE

        elif field == 'description':
            user.state = 'listen_product_photo_' + str(product_id)
            product.description = message.text
            message = ADD_PRODUCT_PHOTO_MESSAGE

        elif field == 'photo':
            if await product.photos.all():
                product.active = True
                user.state = ''
                if not edit:
                    photos = await product.photos
                    await bot.send_media_group(
                        message.from_user.id,
                        [InputMediaPhoto(photo) for photo in photos]
                    )
                message = SELLER_INFO_PRODUCT_MESSAGE.format(
                    name=product.name, description=product.description
                )
                keyboard = await get_seller_product_info_keyboard(product, shop)
                await user.save()

        await product.save()

        if edit:
            user.state = ''
            message = SAVED_MESSAGE
            keyboard = get_go_seller_product_keyboard(product, shop)

        await user.save()
        await message_.answer(
            message,
            reply_markup=keyboard
        )

    else:
        await message_.delete()


@dp.message_handler(content_types=['photo'])
async def handle_photo(message: types.Message):
    user = await TelegramUser.get_or_none(telegram_id=message.chat.id)
    if user is None:
        return

    photo = message.photo[-1]
    name = f'files/{message.from_user.id}_{photo.file_id}.jpg'
    await photo.download(destination_file=name)

    photo_binary = open(name, 'rb').read()
    os.remove(name)

    if 'listen_shop_photo_' in user.state:
        shop = await Shop.get_or_none(id=int(user.state.replace('listen_shop_photo_', '')))
        if shop is None:
            return

        shop.photo = photo_binary
        await shop.save()

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

    elif 'change_shop_photo_' in user.state:
        shop = await Shop.get_or_none(id=int(user.state.replace('change_shop_photo_', '')))
        if shop is None:
            return

        await message.answer(
            SHOP_CREATED_MESSAGE,
            reply_markup=get_go_seller_shop_info_keyboard(shop)
        )

        await bot.send_photo(
            ADMIN_ID,
            photo=photo_binary,
            caption=ADMIN_EDIT_SHOP_PHOTO_MESSAGE,
            reply_markup=get_admin_edit_shop_keyboard(shop, 'photo')
        )

    elif 'listen_product_photo_' in user.state:
        product = await Product.get_or_none(id=user.state.split('_')[-1])
        if product is None:
            return

        if len(await product.photos.all()) < 3:
            await Photo.create(source=photo_binary, product=product)

    else:
        await message.delete()


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

    if action != 'answer':
        await bot.delete_message(ADMIN_ID, callback.message.message_id)
        shop = await Shop.get_or_none(id=int(param))
        if shop is None:
            return

    if action == 'answer':
        user.state = 'admin_answer_' + param
        await user.save()
        await bot.send_message(
            callback.from_user.id,
            ADMIN_WRITE_MESSAGE
        )

    elif action == 'apply':
        shop.active = True
        await shop.save()

        await bot.send_message(
            (await shop.owner).telegram_id,
            SHOP_ACTIVATED_MESSAGE.format(name=shop.name)
        )

    elif action == 'decline':
        await shop.delete()
        await shop.save()

        await bot.send_message(
            (await shop.owner).telegram_id,
            SHOP_DECLINED_MESSAGE.format(name=shop.name)
        )
    elif 'apply_' in action or 'decline_' in action:
        action, field = action.split('_')

        if action == 'decline':
            await bot.send_message(
                (await shop.owner).telegram_id,
                SHOP_DECLINED_MESSAGE.format(name=shop.name)
            )
        else:
            if field == 'name':
                shop.name = parse(
                    ADMIN_EDIT_SHOP_NAME_MESSAGE.replace('<b>', '').replace('</b>', ''),
                    callback.message.text
                )['name']

            elif field == 'description':
                shop.description = parse(
                    ADMIN_EDIT_SHOP_DESCRIPTION_MESSAGE.replace('<b>', '').replace('</b>', ''),
                    callback.message.text
                )['description']

            elif field == 'photo':
                photo = callback.message.photo[-1]
                name = f'files/{callback.message.from_user.id}_{photo.file_id}.jpg'
                await photo.download(destination_file=name)

                photo_binary = open(name, 'rb').read()
                os.remove(name)
                shop.photo = photo_binary

            await shop.save()
            await bot.send_message(
                (await shop.owner).telegram_id,
                SHOP_ACTIVATED_MESSAGE.format(name=shop.name)
            )


@dp.callback_query_handler(seller_callback.filter())
@dp.throttled(rate=FLOOD_RATE)
async def seller_handler(callback: types.CallbackQuery, callback_data):
    user = await TelegramUser.get_or_none(telegram_id=callback.from_user.id)

    if user is None:
        return

    action = callback_data.get('action')
    shop = callback_data.get('shop')

    if shop != '':
        shop = await Shop.get_or_none(id=int(shop))
        if shop is None:
            return

    if 'shop_cat_' in action or 'edit_cat_' in action or\
            'delete_cat_' in action or 'new_product_' in action or 'products_' in action:
        category = await CategoryShop.get_or_none(id=int(action.split('_')[-1]))

        if category is None:
            return

        elif 'shop_cat_' in action:
            await check_creating(user)
            message = SELLER_INFO_CATEGORY_MESSAGE.format(name=category.name)
            keyboard = get_seller_category_keyboard(shop, category)

        elif 'edit_cat_' in action:
            user.state = 'listen_category_name_' + str(shop.id) + '_' + str(category.id)
            await user.save()
            message = ADD_CATEGORY_MESSAGE
            keyboard = get_go_seller_category_keyboard(shop, category)

        elif 'confirm_delete_cat_' in action:
            await category.delete()
            message = DELETED_MESSAGE
            keyboard = get_go_seller_categories_keyboard(shop)

        elif 'delete_cat_' in action:
            await callback.answer(DELETE_CATEGORY_ALERT, show_alert=True)
            message = DELETE_CONFIRM_MESSAGE
            keyboard = get_seller_delete_category_keyboard(shop, category)

        elif 'products_' in action:
            await check_creating(user)
            message = SELLER_PRODUCTS_MESSAGE.format(name=category.name)
            keyboard = await get_seller_products_keyboard(shop, category)

        elif 'new_product_' in action:
            product = await Product.create(
                category=category,
                name='',
                description=''
            )
            user.state = f'listen_product_name_{product.id}'
            await user.save()
            message = ADD_PRODUCT_MESSAGE
            keyboard = get_go_seller_products_keyboard(shop, category)

        else:
            return

    elif 'product_' in action:
        product = await Product.get_or_none(id=int(user.state.split('_')[-1]))
        if product is None:
            return

        if '_product_' in action:
            field, _, product_id = user.state.split('_')
            user.state = f'edit_listen_product_{field}_{product_id}'
            await user.save()

            keyboard = get_go_seller_product_keyboard(product, shop)

            if field == 'name':
                message = ADD_PRODUCT_MESSAGE

            elif field == 'description':
                message = ADD_PRODUCT_DESCRIPTION_MESSAGE

            elif field == 'photo':
                await callback.answer(DELETE_PHOTO_ALERT, show_alert=True)
                message = DELETE_CONFIRM_MESSAGE
                keyboard = get_seller_add_photo_product_keyboard(product, shop)

            elif field == 'deletephoto':
                photos = await product.photos.all()
                for photo in photos:
                    await photo.delete()
                message = ADD_PRODUCT_PHOTO_MESSAGE

            elif field == 'delete':
                await callback.answer(DELETE_PRODUCT_ALERT, show_alert=True)
                message = DELETE_CONFIRM_MESSAGE
                keyboard = get_delete_product_keyboard(product, shop)

            elif field == 'confirmdelete':
                category = await product.category
                await product.delete()
                message = DELETED_MESSAGE
                keyboard = get_go_seller_products_keyboard(shop, category)

            else:
                return

        else:
            photos = await product.photos
            await bot.send_media_group(
                callback.from_user.id,
                [InputMediaPhoto(photo) for photo in photos]
            )
            message = SELLER_INFO_PRODUCT_MESSAGE.format(
                name=product.name, description=product.description
            )
            keyboard = await get_seller_product_info_keyboard(product, shop)

    elif action == 'open_shop':
        message = CREATE_SHOP_TYPE_MESSAGE
        keyboard = create_type_shop_keyboard

    elif action == 'categories':
        message = SELLER_SHOP_CATEGORIES_MESSAGE
        keyboard = await get_seller_shop_categories_keyboard(shop)

    elif action == 'add_cat':
        user.state = 'listen_category_name_' + str(shop.id) + '_'
        await user.save()
        message = ADD_CATEGORY_MESSAGE
        keyboard = get_go_seller_shop_info_keyboard(shop)

    elif action == 'delete':
        await callback.answer(
            DELETE_SHOP_ALERT,
            show_alert=True
        )
        message = DELETE_CONFIRM_MESSAGE
        keyboard = get_seller_shop_delete_keyboard(shop)

    elif action == 'delete_confirm':
        await shop.delete()
        message = DELETED_MESSAGE
        keyboard = seller_main_menu_keyboard

    elif action == 'info':
        user.state = ''
        await user.save()

        await callback.answer()
        await bot.send_photo(
            user.telegram_id,
            photo=shop.photo
        )
        await bot.send_message(
            user.telegram_id,
            SELLER_INFO_SHOP_MESSAGE.format(
                name=shop.name, description=shop.description
            ),
            reply_markup=get_seller_shop_info_keyboard(shop)
        )
        return

    elif 'change_shop_' in action:
        await callback.answer()

        if action == 'change_shop_name':
            user.state = 'change_shop_' + str(shop.id) + '_' + 'name'
            message = EDIT_NAME_MESSAGE

        elif action == 'change_shop_description':
            user.state = 'change_shop_' + str(shop.id) + '_' + 'description'
            message = EDIT_DESCRIPTION_MESSAGE

        elif action == 'change_shop_photo':
            user.state = 'change_shop_photo_' + str(shop.id)
            message = EDIT_PHOTO_MESSAGE

        else:
            return

        await user.save()
        keyboard = get_go_seller_shop_info_keyboard(shop)

    elif action == 'create_catalog' or action == 'create_bid':
        shop = await Shop.create(
            owner=user,
            name='',
            description='',
            catalog=True if action == 'create_catalog' else False
        )
        user.state = 'create_shop_' + str(shop.id)
        await user.save()
        message = CREATE_SHOP_CATEGORY_MESSAGE
        keyboard = await get_seller_categories_keyboard(shop.id)

    elif 'select_cat_' in action:
        category = await Category.get_or_none(id=int(action.split('_')[-1]))
        if category is None:
            return
        shop.category = category
        await shop.save()

        user.state = 'listen_shop_name_' + str(shop.id)
        await user.save()
        message = INPUT_SHOP_NAME_MESSAGE
        keyboard = seller_main_menu_keyboard

    elif action == 'main':
        await check_creating(user)
        message = MENU_MESSAGE
        keyboard = await get_seller_keyboard(user)

    else:
        return

    await callback.answer()
    await bot.edit_message_text(
        message,
        user.telegram_id,
        callback.message.message_id,
        reply_markup=keyboard
    )


async def check_creating(user):
    if 'create_shop_' in user.state or \
            'listen_shop_name_' in user.state or \
            'listen_shop_description_' in user.state or \
            'listen_shop_photo_' in user.state:
        shop = await Shop.get_or_none(id=int(user.state.split('_')[-1]))
        if shop is None:
            return
        await shop.delete()
        user.state = ''
        await user.save()

    elif 'listen_product_' in user.state and 'edit' not in user.state:
        product_id = int(user.state.split('_')[-1])
        product = await Product.get_or_none(id=product_id)
        if product is None:
            return
        await product.delete()
