from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from data.buttons import *
from db.models import TelegramUser, Category, Shop

start_callback = CallbackData("main_menu", 'select')
admin_callback = CallbackData("admin", 'action', 'param')
seller_callback = CallbackData("seller", 'action', 'shop')


back_to_main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=MAIN_MENU_BUTTON, callback_data=start_callback.new(select='main')),
        ]
    ]
)

support_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=ADMIN_MESSAGE_BUTTON, callback_data=start_callback.new(select='admin_message')),
        ],
        [
            InlineKeyboardButton(text=MAIN_MENU_BUTTON, callback_data=start_callback.new(select='main'))
        ]
    ]
)

create_type_shop_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=CREATE_CATALOG_SHOP_BUTTON, callback_data=seller_callback.new(
                action='create_catalog', shop=''
            )),
            InlineKeyboardButton(text=CREATE_BID_SHOP_BUTTON, callback_data=seller_callback.new(
                action='create_bid', shop=''
            ))
        ],
        [
            InlineKeyboardButton(text=BACK_BUTTON, callback_data=seller_callback.new(
                action='main', shop=''
            ))
        ]
    ]
)

seller_main_menu_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=BACK_BUTTON, callback_data=seller_callback.new(
                action='main', shop=''
            ))
        ]
    ]
)


def get_admin_answer_keyboard(from_user: TelegramUser):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=ANSWER_BUTTON, callback_data=admin_callback.new(
                    action='answer', param=str(from_user.telegram_id)
                )),
            ]
        ]
    )
    return keyboard


def get_admin_shop_keyboard(shop: Shop):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=APPLY_BUTTON, callback_data=admin_callback.new(
                    action='apply', param=str(shop.id)
                )),
                InlineKeyboardButton(text=DECLINE_BUTTON, callback_data=admin_callback.new(
                    action='decline', param=str(shop.id)
                )),
            ]
        ]
    )
    return keyboard


async def get_start_keyboard(user: TelegramUser):
    if not await user.shops.all():
        button = SELLER_BUTTON
    else:
        button = MY_SHOP_BUTTON

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=SHOPS_BUTTON, callback_data=start_callback.new(select='shops')),
                InlineKeyboardButton(text=SERVICES_BUTTON, callback_data=start_callback.new(select='services')),
            ],
            [
                InlineKeyboardButton(text=button, callback_data=start_callback.new(select='seller')),
            ],
            [
                InlineKeyboardButton(text=ABOUT_BUTTON, callback_data=start_callback.new(select='about')),
                InlineKeyboardButton(text=SUPPORT_BUTTON, callback_data=start_callback.new(select='support')),
            ]
        ]
    )
    return keyboard


async def get_seller_keyboard(user):
    shops = await user.shops.filter(active=True)

    shops_buttons = [
        [InlineKeyboardButton(
            text=shop.name, callback_data=seller_callback.new(action='info', shop=str(shop.id))
        )] for shop in shops
    ]

    if len(shops_buttons) < 5:
        shops_buttons.append(
            [InlineKeyboardButton(text=OPEN_SHOP_BUTTON, callback_data=seller_callback.new(
                action='open_shop', shop=''
            ))]
        )

    shops_buttons.append(
        [
            InlineKeyboardButton(text=MAIN_MENU_BUTTON, callback_data=start_callback.new(select='main')),
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=shops_buttons)
    return keyboard


async def get_seller_categories_keyboard(shop_id):
    categories = await Category.all()
    inline_keyboard = []

    for i in range(0, len(categories), 2):
        if i != len(categories) - 1:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(text=BACK_BUTTON, callback_data=seller_callback.new(
                        action=f'select_cat_{categories[i].id}', shop=str(shop_id)
                    )),
                    InlineKeyboardButton(text=BACK_BUTTON, callback_data=seller_callback.new(
                        action=f'select_cat_{categories[i+1].id}', shop=str(shop_id)
                    )),
                ]
            )
        else:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(text=BACK_BUTTON, callback_data=seller_callback.new(
                        action=f'select_cat_{categories[i].id}', shop=str(shop_id)
                    ))
                ]
            )

    inline_keyboard.append(
        [
            InlineKeyboardButton(text=BACK_BUTTON, callback_data=seller_callback.new(
                action='main', shop=''
            ))
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard
