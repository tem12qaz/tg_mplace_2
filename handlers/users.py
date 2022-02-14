import io
import os
import asyncio

from aiogram import types
from aiogram.dispatcher.filters import CommandStart, CommandHelp
from aiogram.types import InputMediaPhoto, InputFile
from parse import parse

from data.config import FLOOD_RATE, ADMIN_ID, ADMINS, CHANNEL
from db.models import TelegramUser, Shop, Product, Photo, Deal, Review, Category, CategoryShop, ServiceCategory, Form, \
    Bid
from data.messages import *
from keyboards.inline.keyboards import start_callback, back_to_main_menu_keyboard, support_keyboard, \
    get_admin_answer_keyboard, admin_callback, get_start_keyboard, get_seller_keyboard, seller_callback, \
    create_type_shop_keyboard, get_seller_categories_keyboard, seller_main_menu_keyboard, get_admin_shop_keyboard, \
    get_seller_shop_info_keyboard, get_go_seller_shop_info_keyboard, get_admin_edit_shop_keyboard, \
    get_seller_shop_delete_keyboard, get_seller_shop_categories_keyboard, get_go_seller_categories_keyboard, \
    get_seller_category_keyboard, get_go_seller_category_keyboard, get_seller_delete_category_keyboard, \
    get_seller_products_keyboard, get_go_seller_products_keyboard, get_go_seller_product_keyboard, \
    get_seller_product_info_keyboard, get_seller_add_photo_product_keyboard, get_delete_product_keyboard, \
    get_service_categories_keyboard, get_shops_keyboard, get_shop_keyboard, get_back_shop_keyboard, \
    get_shops_cats_keyboard, get_shops_prods_keyboard, get_prod_keyboard, get_categories_keyboard, get_review_keyboard, \
    get_back_to_prod_keyboard, get_reviews_keyboard, get_confirm_delete_form_keyboard, get_create_form_keyboard, \
    get_form_shop_keyboard
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
        )
        await message.answer(
            START_MESSAGE,
            reply_markup=await get_start_keyboard(user)
        )
        return

    await check_creating(user)

    await message.answer(
        MAIN_MENU_MESSAGE,
        reply_markup=await get_start_keyboard(user)
    )


@dp.message_handler(commands=['mail'])
@dp.throttled(rate=FLOOD_RATE)
async def mail_handler(message: types.Message):
    if int(message.from_user.id) not in ADMINS:
        await message.delete()
        return

    user = await TelegramUser.get_or_none(telegram_id=message.from_user.id)
    if user is None:
        return

    await check_creating(user)

    user.state = 'mail'
    await user.save()
    await message.answer(
        MAIL_MESSAGE,
        reply_markup=back_to_main_menu_keyboard
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
        await bot.edit_message_text(
            CREATE_SHOP_CATEGORY_MESSAGE,
            user.telegram_id,
            callback.message.message_id,
            reply_markup=await get_categories_keyboard()
        )

    elif select == 'services':
        await bot.edit_message_text(
            CREATE_SHOP_CATEGORY_MESSAGE,
            user.telegram_id,
            callback.message.message_id,
            reply_markup=await get_service_categories_keyboard()
        )

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
        await check_creating(user)
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

    elif 'service_' in select:
        category = await ServiceCategory.get_or_none(id=int(select.replace('service_', '')))
        if category is None:
            return
        user.state = f'service_{category.id}'
        await user.save()
        await bot.edit_message_text(
            SERVICE_DEAL_MESSAGE,
            user.telegram_id,
            callback.message.message_id,
            reply_markup=back_to_main_menu_keyboard
        )

    elif 'shop_cat_' in select:
        await check_creating(user)
        category = await CategoryShop.get_or_none(id=int(select.split('_')[-1]))
        if category is None:
            return

        await bot.edit_message_text(
            SELECT_PRODUCT_MESSAGE,
            user.telegram_id,
            callback.message.message_id,
            reply_markup=await get_shops_prods_keyboard(category)
        )

    elif 'cat_' in select:
        category = await Category.get_or_none(id=int(select.replace('cat_', '')))
        if category is None:
            return

        await bot.edit_message_text(
            SELECT_SHOP_MESSAGE,
            user.telegram_id,
            callback.message.message_id,
            reply_markup=await get_shops_keyboard(category)
        )

    elif 'deal_prod_' in select:
        await check_creating(user)
        product = await Product.get_or_none(id=int(select.split('_')[-1]))
        if product is None:
            return

        shop = await (await product.category).shop
        if shop is None:
            return

        user.state = f'contacts_{product.id}'
        await user.save()

        await bot.edit_message_text(
            CONTACTS_MESSAGE,
            user.telegram_id,
            callback.message.message_id,
            reply_markup=get_back_to_prod_keyboard(product)
        )

    elif 'reviews_prod_' in select:
        await check_creating(user)
        product = await Product.get_or_none(id=int(select.split('_')[-1]))
        if product is None:
            return

        if '>reviews_prod' in select:
            review = await Review.get_or_none(id=int(select.split('_')[0]))
            if review is None:
                return
            reviews = await product.reviews.all()
            try:
                review = reviews[reviews.index(review) + 1]
            except:
                review = await reviews[0]

        elif '<reviews_prod' in select:
            review = await Review.get_or_none(id=int(select.split('_')[0]))
            if review is None:
                return
            reviews = await product.reviews.all()
            try:
                review = reviews[reviews.index(review) - 1]
            except:
                review = await reviews[-1]
        else:
            reviews = await product.reviews.all()
            if reviews:
                review = await reviews[0]
            else:
                review = None

        keyboard = get_back_to_prod_keyboard(product)
        if review:
            message = REVIEWS_MESSAGE.format(rating=review.rating, text=review.text)
            if len(reviews) != 1:
                keyboard = get_reviews_keyboard(product, review)
        else:
            message = 'Нет отзывов'

        await bot.edit_message_text(
            message,
            user.telegram_id,
            callback.message.message_id,
            reply_markup=keyboard
        )

    elif 'review_prod_' in select:
        await check_creating(user)
        product = await Product.get_or_none(id=int(select.split('_')[-1]))
        if product is None:
            return

        await bot.edit_message_text(
            RATE_PRODUCT_MESSAGE,
            user.telegram_id,
            callback.message.message_id,
            reply_markup=get_review_keyboard(product)
        )

    elif 'shop_prod_' in select:
        await check_creating(user)
        product = await Product.get_or_none(id=int(select.split('_')[-1]))
        if product is None:
            return

        await send_product_photos(user, product)
        message = INFO_PRODUCT_MESSAGE.format(
            name=product.name, description=product.description, price=product.price
        )
        reviews = await product.reviews.all()
        if reviews:
            rating = 0
            for review in reviews:
                rating += review.rating
            rating = round(rating / len(reviews), 2)
            message += RATING.format(rating=rating)
        keyboard = await get_prod_keyboard(product)
        await bot.send_message(
            user.telegram_id,
            message,
            reply_markup=keyboard
        )

    elif 'rate_prod_' in select:
        await check_creating(user)
        product = await Product.get_or_none(id=int(select.split('_')[-1]))
        if product is None:
            return

        user.state = select
        await user.save()

        await bot.edit_message_text(
            RATE_PRODUCT_TEXT_MESSAGE,
            user.telegram_id,
            callback.message.message_id,
            reply_markup=get_back_to_prod_keyboard(product)
        )

    elif 'shop_' in select:
        await check_creating(user)
        shop = await Shop.get_or_none(id=int(select.split('_')[-1]))
        if shop is None:
            return

        if 'shop_free_' in select:
            user.state = f'shop_deal_{shop.id}'
            await user.save()
            await bot.edit_message_text(
                SERVICE_DEAL_MESSAGE,
                user.telegram_id,
                callback.message.message_id,
                reply_markup=get_back_shop_keyboard(shop)
            )
        elif 'shop_deal_' in select:
            if await shop.form:
                await bot.edit_message_text(
                    SELECT_FORM_MESSAGE,
                    user.telegram_id,
                    callback.message.message_id,
                    reply_markup=get_form_shop_keyboard(shop)
                )
            else:
                await bot.edit_message_text(
                    SERVICE_DEAL_MESSAGE,
                    user.telegram_id,
                    callback.message.message_id,
                    reply_markup=get_back_shop_keyboard(shop)
                )

        elif 'shop_field_' in select:
            form = await shop.form
            if form is None:
                return

            user.state = f'{form.id}_create_bid'
            await user.save()
            await bot.edit_message_text(
                SEND_MESSAGE + form.field1,
                user.telegram_id,
                callback.message.message_id,
                reply_markup=get_back_shop_keyboard(shop)
            )
        elif 'shop_cats_' in select:
            await bot.edit_message_text(
                SELECT_CAT_MESSAGE,
                user.telegram_id,
                callback.message.message_id,
                reply_markup=await get_shops_cats_keyboard(shop)
            )

        else:
            await check_creating(user)
            message = INFO_SHOP_MESSAGE.format(
                name=shop.name, description=shop.description
            )

            reviews = await shop.reviews.all()
            if reviews:
                rating = 0
                for review in reviews:
                    rating += review.rating
                rating = rating / len(reviews)
                message += RATING.format(rating=rating)

            await bot.send_photo(
                user.telegram_id,
                photo=shop.photo
            )
            await bot.send_message(
                user.telegram_id,
                message,
                reply_markup=await get_shop_keyboard(shop)
            )
    else:
        return


@dp.message_handler()
@dp.throttled(rate=FLOOD_RATE)
async def listen_handler(message: types.Message):
    print('e')
    message_ = message
    user = await TelegramUser.get_or_none(telegram_id=message.from_user.id)
    if user is None:
        return

    if user.state is None:
        await message.delete()

    elif 'create_bid' in user.state:
        if 'create_bid_' in user.state:
            bid = await Bid.get_or_none(id=int(user.state.split('_')[-1]))
            if bid is None:
                return
            form = await bid.form
            if form is None:
                return
            shop = await form.shop
            if shop is None:
                return

            async def send_deal(bid_):
                user.state = ''
                await user.save()
                channel_ = (await shop.category).channel
                text_ = ''
                fields = form.fields()
                for field_ in fields:
                    if field_:
                        text_ += BID_ROW.format(
                            field=field_,
                            value=bid_.fields()[fields.index(field_)]
                        )

                await message.answer(
                    DEAL_CREATED_MESSAGE,
                    reply_markup=get_back_shop_keyboard(shop)
                )
                await bot.send_message(
                    channel_,
                    SHOP_DEAL_MESSAGE.format(
                        shop=shop.name,
                        username=user.username,
                        text=text_
                    )
                )

                await bot.send_message(
                    (await shop.owner).telegram_id,
                    SHOP_DEAL_MESSAGE.format(
                        shop=shop.name,
                        username=user.username,
                        text=text_
                    )
                )
                await bid_.delete()

            keyboard = get_back_shop_keyboard(shop)

            if bid.field4:
                bid.field5 = message.text[:1024]
                await send_deal(bid)
                return

            elif bid.field3:
                bid.field4 = message.text[:1024]
                text = SEND_MESSAGE + form.field5
                if not form.field5:
                    await send_deal(bid)
                    return

            elif bid.field2:
                bid.field3 = message.text[:1024]
                text = SEND_MESSAGE + form.field4
                if not form.field4:
                    await send_deal(bid)
                    return

            elif bid.field1:
                bid.field2 = message.text[:1024]
                text = SEND_MESSAGE + form.field3
                if not form.field3:
                    await send_deal(bid)
                    return
            else:
                return

            await bid.save()
            await message.answer(
                text,
                reply_markup=keyboard
            )

        else:
            form_id = user.state.split('_')[0]
            form = await Form.get_or_none(id=int(form_id))
            if form is None:
                return
            bid = await Bid.create(form=form, field1=message.text[:1024])
            user.state = f'create_bid_{bid.id}'
            await user.save()
            await message.answer(
                SEND_MESSAGE + form.field2,
                reply_markup=get_back_shop_keyboard(await form.shop)
            )

    elif 'create_form' in user.state:
        if 'create_form_' in user.state:
            form = await Form.get_or_none(id=int(user.state.split('_')[-1]))
            if form is None:
                return
            shop = await form.shop
            if shop is None:
                return

            keyboard = get_create_form_keyboard(shop, form)
            if form.field4:
                form.field5 = message.text[:256]
                text = FORM_SAVED_MESSAGE
                keyboard = get_go_seller_shop_info_keyboard(shop)
                user.state = ''
                await user.save()
            elif form.field3:
                form.field4 = message.text[:256]
                text = CREATE_FORM5_MESSAGE
            elif form.field2:
                form.field3 = message.text[:256]
                text = CREATE_FORM4_MESSAGE
            elif form.field1:
                form.field2 = message.text[:256]
                text = CREATE_FORM3_MESSAGE
            else:
                return

            await form.save()
            await message.answer(
                text,
                reply_markup=keyboard
            )

        else:
            shop_id = user.state.split('_')[0]
            shop = await Shop.get_or_none(id=int(shop_id))
            if shop is None:
                return
            form = await Form.create(shop=shop, field1=message.text[:256])
            user.state = f'create_form_{form.id}'
            await user.save()
            await message.answer(
                CREATE_FORM2_MESSAGE,
                reply_markup=get_create_form_keyboard(shop, form)
            )

    elif 'mail' in user.state:
        users = await TelegramUser.all()
        photos = []
        if '_' in user.state:
            photo = await Photo.get_or_none(id=int(user.state.replace('mail_', '')))
            if photo is None:
                user.state = ''

        for user in users:
            if '_' in user.state:
                await bot.send_photo(
                    user.telegram_id,
                    photo=photo.source
                )
            await bot.send_message(
                user.telegram_id,
                message.text
            )
        user.state = ''
        await user.save()
        await message.answer(
            MAILED_MESSAGE
        )

    elif user.state == 'admin_message':
        user.state = ''
        await user.save()
        await bot.send_message(
            CHANNEL,
            ADMIN_READ_MESSAGE.format(message=message.text),
            reply_markup=get_admin_answer_keyboard(user)
        )
        await message.answer(
            ADMIN_SENT_MESSAGE,
            reply_markup=back_to_main_menu_keyboard
        )

    elif 'contacts_' in user.state:
        product = await Product.get_or_none(id=int(user.state.replace('contacts_', '')))
        shop = await (await product.category).shop
        channel = (await shop.category).channel
        if product is None or shop is None:
            return

        await message.answer(
            DEAL_CREATED_MESSAGE,
            reply_markup=get_back_to_prod_keyboard(product)
        )

        await bot.send_message(
            channel,
            PRODUCT_DEAL_MESSAGE.format(
                shop=shop.name,
                username=user.username,
                product=product.name,
                price=product.price,
                contacts=message.text[:3000]
            )
        )

        await bot.send_message(
            (await shop.owner).telegram_id,
            PRODUCT_DEAL_MESSAGE.format(
                shop=shop.name,
                username=user.username,
                product=product.name,
                price=product.price,
                contacts=message.text[:3000]
            )
        )
        user.state = ''
        await user.save()

    elif 'service_' in user.state:
        category = await ServiceCategory.get_or_none(id=int(user.state.replace('service_', '')))
        if category is None:
            return

        channel = category.channel

        await message.answer(
            DEAL_CREATED_MESSAGE,
            reply_markup=back_to_main_menu_keyboard
        )

        await bot.send_message(
            channel,
            ADMIN_SERVICE_MESSAGE.format(
                category=category.name,
                username=user.username,
                text=message.text
            )
        )

        user.state = ''
        await user.save()

    elif 'rate_prod_' in user.state:
        rating, product_id = user.state.replace('rate_prod_', '').split('_')
        user.state = ''
        await user.save()

        product = await Product.get_or_none(id=int(product_id))
        if product is None:
            return

        await Review.create(
            product=product,
            shop=await (await product.category).shop,
            customer=user,
            text=message.text[:3900],
            rating=int(rating)
        )
        await message.answer(
            REVIEW_CREATED_MESSAGE,
            reply_markup=get_back_to_prod_keyboard(product)
        )

    elif 'shop_deal_' in user.state:
        shop = await Shop.get_or_none(id=int(user.state.replace('shop_deal_', '')))
        if shop is None:
            return

        channel = (await shop.category).channel

        await message.answer(
            DEAL_CREATED_MESSAGE,
            reply_markup=get_back_shop_keyboard(shop)
        )
        await bot.send_message(
            channel,
            SHOP_DEAL_MESSAGE.format(
                shop=shop.name,
                username=user.username,
                text=message.text
            )
        )

        await bot.send_message(
            (await shop.owner).telegram_id,
            SHOP_DEAL_MESSAGE.format(
                shop=shop.name,
                username=user.username,
                text=message.text
            )
        )
        user.state = ''
        await user.save()

    elif 'admin_answer' in user.state:
        state = user.state
        user.state = ''
        await user.save()
        # if int(user.telegram_id) not in ADMINS:
        #     return

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
            CHANNEL,
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
            user.state = user.state.replace('edit_', '')
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
            user.state = 'listen_product_price_' + str(product_id)
            product.description = message.text
            message = ADD_PRODUCT_PRICE_MESSAGE

        elif field == 'price':
            user.state = 'listen_product_photo_' + str(product_id)
            try:
                product.price = int(message.text)
            except:
                await message.delete()
                return

            message = ADD_PRODUCT_PHOTO_MESSAGE

        elif field == 'photo':
            if await product.photos.all():
                product.active = True
                user.state = ''
                if not edit:
                    await send_product_photos(user, product)
                    message = SELLER_INFO_PRODUCT_MESSAGE.format(
                        name=product.name, description=product.description, price=product.price
                    )
                    keyboard = await get_seller_product_info_keyboard(product, shop)
                    await bot.send_message(
                        user.telegram_id,
                        message,
                        reply_markup=keyboard
                    )
                    await user.save()
                    await product.save()

                    return

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
            CHANNEL,
            photo=photo_binary,
            caption=ADMIN_CREATE_SHOP_MESSAGE.format(
                name=shop.name, description=shop.description
            ),
            reply_markup=get_admin_shop_keyboard(shop)
        )

    elif 'mail' in user.state:
        if len(user.state.split('_')) > 2:
            await message.delete()
            return
        photo = await Photo.create(source=photo_binary)

        user.state = user.state + '_' + str(photo.id)
        await user.save()
        return

    elif 'change_shop_photo_' in user.state:
        shop = await Shop.get_or_none(id=int(user.state.replace('change_shop_photo_', '')))
        if shop is None:
            return

        await message.answer(
            SHOP_CREATED_MESSAGE,
            reply_markup=get_go_seller_shop_info_keyboard(shop)
        )

        await bot.send_photo(
            CHANNEL,
            photo=photo_binary,
            caption=ADMIN_EDIT_SHOP_PHOTO_MESSAGE,
            reply_markup=get_admin_edit_shop_keyboard(shop, 'photo')
        )

    user = await TelegramUser.get_or_none(telegram_id=message.chat.id)
    if user is None:
        return

    elif 'listen_product_photo_' in user.state or 'listen_product_delphoto_' in user.state:
        product = await Product.get_or_none(id=user.state.split('_')[-1])
        if product is None:
            return

        if 'listen_product_delphoto_' in user.state:
            user.state = f'listen_product_photo_{product.id}'
            await user.save()
            photos = await product.photos.all()
            for photo in photos:
                await photo.delete()
        else:
            await asyncio.sleep(1)

        if len(await product.photos.all()) < 3:
            await Photo.create(source=photo_binary, product=product)

    else:
        await message.delete()


@dp.message_handler(content_types=['document'])
async def handle_docs(message: types.Message):
    user = await TelegramUser.get_or_none(telegram_id=message.chat.id)
    if user is None:
        return

    photo = message.document
    # print(message.document)
    print(photo)
    if 'jpg' not in photo['mime_type'] and \
            'jpeg' not in photo['mime_type'] and \
            'png' not in photo['mime_type']:
        await message.delete()
        return

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
            CHANNEL,
            photo=photo_binary,
            caption=ADMIN_CREATE_SHOP_MESSAGE.format(
                name=shop.name, description=shop.description
            ),
            reply_markup=get_admin_shop_keyboard(shop)
        )

    elif 'mail' in user.state:
        if len(user.state.split('_')) > 2:
            await message.delete()
            return
        photo = await Photo.create(source=photo_binary)

        user.state = user.state + '_' + str(photo.id)
        await user.save()
        return

    elif 'change_shop_photo_' in user.state:
        shop = await Shop.get_or_none(id=int(user.state.replace('change_shop_photo_', '')))
        if shop is None:
            return

        await message.answer(
            SHOP_CREATED_MESSAGE,
            reply_markup=get_go_seller_shop_info_keyboard(shop)
        )

        await bot.send_photo(
            CHANNEL,
            photo=photo_binary,
            caption=ADMIN_EDIT_SHOP_PHOTO_MESSAGE,
            reply_markup=get_admin_edit_shop_keyboard(shop, 'photo')
        )

    elif 'listen_product_photo_' in user.state or 'listen_product_delphoto_' in user.state:
        product = await Product.get_or_none(id=user.state.split('_')[-1])
        if product is None:
            return

        user = await TelegramUser.get_or_none(telegram_id=message.chat.id)
        if user is None:
            return

        if 'listen_product_delphoto_' in user.state:
            user.state = f'listen_product_photo_{product.id}'
            await user.save()
            photos = await product.photos.all()
            for photo in photos:
                await photo.delete()

        else:
            await asyncio.sleep(1)

        if len(await product.photos.all()) < 3:
            print('wedewd')
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
    # elif int(user.telegram_id) not in :
    #     return

    action = callback_data.get('action')
    param = callback_data.get('param')

    if action != 'answer':
        await bot.delete_message(CHANNEL, callback.message.message_id)
        shop = await Shop.get_or_none(id=int(param))
        if shop is None:
            return

    if action == 'answer':
        user.state = 'admin_answer_' + param
        await user.save()
        await bot.send_message(
            callback.message.chat.id,
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

    if 'shop_cat_' in action or 'edit_cat_' in action or \
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
                description='',
                price=0
            )
            user.state = f'listen_product_name_{product.id}'
            await user.save()
            message = ADD_PRODUCT_MESSAGE
            keyboard = get_go_seller_products_keyboard(shop, category)

        else:
            return

    elif 'product_' in action:
        product = await Product.get_or_none(id=int(action.split('_')[-1]))
        if product is None:
            return

        if '_product_' in action:
            field, _, product_id = action.split('_')
            if field == 'photo':
                field = 'delphoto'
            user.state = f'edit_listen_product_{field}_{product_id}'
            await user.save()

            keyboard = get_go_seller_product_keyboard(product, shop)

            if field == 'name':
                message = ADD_PRODUCT_MESSAGE

            elif field == 'description':
                message = ADD_PRODUCT_DESCRIPTION_MESSAGE

            elif field == 'price':
                message = ADD_PRODUCT_PRICE_MESSAGE

            elif field == 'delphoto':
                await callback.answer(DELETE_PHOTO_ALERT, show_alert=True)
                message = ADD_PRODUCT_PHOTO_MESSAGE

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
            message = SELLER_INFO_PRODUCT_MESSAGE.format(
                name=product.name, description=product.description, price=product.price
            )
            keyboard = await get_seller_product_info_keyboard(product, shop)
            await send_product_photos(user, product)
            await bot.send_message(
                user.telegram_id,
                message,
                reply_markup=keyboard
            )
            return

    elif action == 'create_form':
        user.state = f'{shop.id}_create_form'
        await user.save()
        message = CREATE_FORM_MESSAGE
        keyboard = get_go_seller_shop_info_keyboard(shop)

    elif action == 'del_form':
        await callback.answer(DELETE_PRODUCT_ALERT, show_alert=True)
        message = DELETE_CONFIRM_MESSAGE
        keyboard = get_confirm_delete_form_keyboard(shop)

    elif action == 'confirm_delete_form':
        form = await shop.form
        await form.delete()
        message = DELETED_MESSAGE
        keyboard = get_go_seller_shop_info_keyboard(shop)

    elif 'save_form_' in action:
        user.state = ''
        await user.save()
        message = FORM_SAVED_MESSAGE
        keyboard = get_go_seller_shop_info_keyboard(shop)

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
        await check_creating(user)
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
            reply_markup=await get_seller_shop_info_keyboard(shop)
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
        user.state = ''
        await user.save()
        if shop is None:
            return
        await shop.delete()

    elif 'listen_product_' in user.state and 'edit' not in user.state:
        product_id = int(user.state.split('_')[-1])
        product = await Product.get_or_none(id=product_id)
        user.state = ''
        await user.save()
        if product is None:
            return
        await product.delete()

    elif 'create_form_' in user.state:
        form_id = int(user.state.split('_')[-1])
        form = await Form.get_or_none(id=form_id)
        user.state = ''
        await user.save()
        if form is None:
            return
        await form.delete()

    elif 'create_bid_' in user.state:
        bid_id = int(user.state.split('_')[-1])
        bid = await Bid.get_or_none(id=bid_id)
        user.state = ''
        await user.save()
        if bid is None:
            return
        await bid.delete()

    else:
        user.state = ''
        await user.save()


async def send_product_photos(user: TelegramUser, product: Product):
    photos = await product.photos.all()

    media = types.MediaGroup()
    for photo in photos:
        media.attach_photo(InputFile(io.BytesIO(photo.source)))

    await bot.send_media_group(
        user.telegram_id,
        media=media
    )
