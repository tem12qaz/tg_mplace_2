from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from data.buttons import *
from db.models import TelegramUser

start_callback = CallbackData("main_menu", 'select')
admin_callback = CallbackData("admin", 'action', 'param')

start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=SHOPS_BUTTON, callback_data=start_callback.new(select='shops')),
            InlineKeyboardButton(text=SELLER_BUTTON, callback_data=start_callback.new(select='seller')),
        ],
        [
            InlineKeyboardButton(text=ABOUT_BUTTON, callback_data=start_callback.new(select='about')),
            InlineKeyboardButton(text=SUPPORT_BUTTON, callback_data=start_callback.new(select='support')),
        ]
    ]
)

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
            InlineKeyboardButton(text=MAIN_MENU_BUTTON, callback_data=start_callback.new(select='main')),
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
