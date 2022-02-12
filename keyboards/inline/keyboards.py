from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from data.buttons import *
from data.messages import CREATE_REVIEW_MESSAGE, REVIEW_MESSAGE
from db.models import TelegramUser, Category, Shop, CategoryShop, Product, ServiceCategory

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

async def get_revies_shop_keyboard(shop: Shop):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='1', callback_data=start_callback.new(
                    select='rate_shop_1'
                )),
                InlineKeyboardButton(text='1', callback_data=start_callback.new(
                    select='rate_shop_2'
                )),
                InlineKeyboardButton(text='1', callback_data=start_callback.new(
                    select='rate_shop_3'
                )),
                InlineKeyboardButton(text='1', callback_data=start_callback.new(
                    select='rate_shop_4'
                )),
                InlineKeyboardButton(text='1', callback_data=start_callback.new(
                    select='rate_shop_5'
                )),
            ],
            [
                InlineKeyboardButton(text=BACK_BUTTON, callback_data=start_callback.new(select=f'cat_{category.id}'))
            ]
        ]
    )
    return keyboard


def get_back_shop_keyboard(shop: Shop):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=BACK_BUTTON, callback_data=start_callback.new(select=f'shop_{shop.id}'))
            ]
        ]
    )
    return keyboard


async def get_prod_keyboard(product: Product):
    category = await product.category
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=DEAL_BUTTON, callback_data=start_callback.new(
                    select=f'deal_prod_{product.id}'
                )),
            ],
            [
                InlineKeyboardButton(text=DEAL_BUTTON, callback_data=start_callback.new(
                    select=f'reviews_prod_{product.id}'
                )),
                InlineKeyboardButton(text=DEAL_BUTTON, callback_data=start_callback.new(
                    select=f'review_prod_{product.id}'
                )),
            ],
            [
                InlineKeyboardButton(text=BACK_BUTTON, callback_data=start_callback.new(select=f'shop_cat_{category.id}'))
            ]
        ]
    )
    return keyboard


async def get_shop_keyboard(shop: Shop):
    category = await shop.category
    if shop.catalog:
        text = CATEGORIES_BUTTON
        select = 'shop_cats_'
    else:
        text = DEAL_BUTTON
        select = 'shop_deal_'

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=text, callback_data=start_callback.new(
                    select=f'{select}{shop.id}'
                )),
            ],
            [
                InlineKeyboardButton(text=BACK_BUTTON, callback_data=start_callback.new(select=f'cat_{category.id}'))
            ]
        ]
    )
    return keyboard


async def get_shops_cats_keyboard(shop: Shop):
    categories = await shop.categories.all()
    inline_keyboard = []
    for i in range(0, len(categories), 2):
        if i != len(categories) - 1:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(text=categories[i].name, callback_data=start_callback.new(
                        select=f'shop_cat_{categories[i].id}'
                    )),
                    InlineKeyboardButton(text=categories[i + 1].name, callback_data=start_callback.new(
                        select=f'shop_cat_{categories[i + 1].id}'
                    )),
                ]
            )
        else:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(text=categories[i].name, callback_data=start_callback.new(
                        select=f'shop_cat_{categories[i].id}'
                    ))
                ]
            )

    inline_keyboard.append(
        [
            InlineKeyboardButton(text=BACK_BUTTON, callback_data=start_callback.new(
                select=f'shop_{shop.id}'
            ))
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard


async def get_shops_prods_keyboard(category: CategoryShop):
    prods = await category.products.all()
    shop = await category.shop
    inline_keyboard = []
    for i in range(0, len(prods), 2):
        if i != len(prods) - 1:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(text=prods[i].name, callback_data=start_callback.new(
                        select=f'shop_prod_{prods[i].id}'
                    )),
                    InlineKeyboardButton(text=prods[i + 1].name, callback_data=start_callback.new(
                        select=f'shop_prod_{prods[i + 1].id}'
                    )),
                ]
            )
        else:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(text=prods[i].name, callback_data=start_callback.new(
                        select=f'shop_prod_{prods[i].id}'
                    ))
                ]
            )

    inline_keyboard.append(
        [
            InlineKeyboardButton(text=BACK_BUTTON, callback_data=start_callback.new(
                select=f'shop_cats_{shop.id}'
            ))
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard


async def get_shops_keyboard(category: Category):
    shops = await Shop.filter(category=category)
    inline_keyboard = []
    for i in range(0, len(shops), 2):
        if i != len(shops) - 1:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(text=shops[i].name, callback_data=start_callback.new(
                        select=f'shop_{shops[i].id}'
                    )),
                    InlineKeyboardButton(text=shops[i + 1].name, callback_data=start_callback.new(
                        select=f'shop_{shops[i + 1].id}'
                    )),
                ]
            )
        else:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(text=shops[i].name, callback_data=start_callback.new(
                        select=f'shops'
                    ))
                ]
            )

    inline_keyboard.append(
        [
            InlineKeyboardButton(text=BACK_BUTTON, callback_data=start_callback.new(
                select=f'cat_{category.id}'
            ))
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard


async def get_categories_keyboard():
    categories = await Category.all()
    inline_keyboard = []

    for i in range(0, len(categories), 2):
        if i != len(categories) - 1:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(text=categories[i].name, callback_data=start_callback.new(
                        select=f'cat_{categories[i].id}'
                    )),
                    InlineKeyboardButton(text=categories[i + 1].name, callback_data=start_callback.new(
                        select=f'cat_{categories[i + 1].id}'
                    )),
                ]
            )
        else:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(text=categories[i].name, callback_data=start_callback.new(
                        select=f'cat_{categories[i].id}'
                    ))
                ]
            )

    inline_keyboard.append(
        [
            InlineKeyboardButton(text=BACK_BUTTON, callback_data=start_callback.new(
                select='main'
            ))
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard


async def get_service_categories_keyboard():
    categories = await ServiceCategory.all()
    inline_keyboard = []

    for i in range(0, len(categories), 2):
        if i != len(categories) - 1:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(text=categories[i].name, callback_data=start_callback.new(
                        select=f'service_{categories[i].id}'
                    )),
                    InlineKeyboardButton(text=categories[i + 1].name, callback_data=start_callback.new(
                        select=f'service_{categories[i + 1].id}'
                    )),
                ]
            )
        else:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(text=categories[i].name, callback_data=start_callback.new(
                        select=f'service_{categories[i].id}'
                    ))
                ]
            )

    inline_keyboard.append(
        [
            InlineKeyboardButton(text=BACK_BUTTON, callback_data=start_callback.new(
                select='main'
            ))
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard


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


def get_admin_edit_shop_keyboard(shop: Shop, field: str):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=APPLY_BUTTON, callback_data=admin_callback.new(
                    action=f'apply_{field}', param=str(shop.id)
                )),
                InlineKeyboardButton(text=DECLINE_BUTTON, callback_data=admin_callback.new(
                    action=f'decline_{field}', param=str(shop.id)
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


def get_go_seller_shop_info_keyboard(shop: Shop):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=BACK_BUTTON, callback_data=seller_callback.new(
                    action='info', shop=str(shop.id)
                ))
            ]
        ]
    )
    return keyboard


def get_seller_category_keyboard(shop: Shop, category: CategoryShop):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=PRODUCTS_BUTTON, callback_data=seller_callback.new(
                    action=f'products_{category.id}', shop=str(shop.id)
                ))
            ],
            [
                InlineKeyboardButton(text=EDIT_NAME_BUTTON, callback_data=seller_callback.new(
                    action=f'edit_cat_{category.id}', shop=str(shop.id)
                ))
            ],
            [
                InlineKeyboardButton(text=DELETE_CATEGORY_BUTTON, callback_data=seller_callback.new(
                    action=f'delete_cat_{category.id}', shop=str(shop.id)
                ))
            ],
            [
                InlineKeyboardButton(text=BACK_BUTTON, callback_data=seller_callback.new(
                    action='categories', shop=str(shop.id)
                ))
            ]
        ]
    )
    return keyboard


def get_seller_delete_category_keyboard(shop: Shop, category: CategoryShop):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=DELETE_BUTTON, callback_data=seller_callback.new(
                    action=f'confirm_delete_cat_{category.id}', shop=str(shop.id)
                ))
            ]
        ]
    )
    return keyboard


def get_go_seller_category_keyboard(shop: Shop, category: CategoryShop):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=BACK_BUTTON, callback_data=seller_callback.new(
                    action=f'shop_cat_{category.id}', shop=str(shop.id)
                ))
            ]
        ]
    )
    return keyboard


def get_go_seller_categories_keyboard(shop: Shop):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=BACK_BUTTON, callback_data=seller_callback.new(
                    action='categories', shop=str(shop.id)
                ))
            ]
        ]
    )
    return keyboard


def get_go_seller_products_keyboard(shop: Shop, category: CategoryShop):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=BACK_BUTTON, callback_data=seller_callback.new(
                    action=f'products_{category.id}', shop=str(shop.id)
                ))
            ]
        ]
    )
    return keyboard


def get_go_seller_product_keyboard(product: Product, shop: Shop):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=BACK_BUTTON, callback_data=seller_callback.new(
                    action=f'product_{product.id}', shop=str(shop.id)
                ))
            ]
        ]
    )
    return keyboard


def get_delete_product_keyboard(product: Product, shop: Shop):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=DELETE_BUTTON, callback_data=seller_callback.new(
                    action=f'confirmdelete_product_{product.id}', shop=str(shop.id)
                ))
            ],
            [
                InlineKeyboardButton(text=BACK_BUTTON, callback_data=seller_callback.new(
                    action=f'product_{product.id}', shop=str(shop.id)
                ))
            ]
        ]
    )
    return keyboard


def get_seller_add_photo_product_keyboard(product: Product, shop: Shop):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=DELETE_BUTTON, callback_data=seller_callback.new(
                    action=f'deletephoto_product_{product.id}', shop=str(shop.id)
                ))
            ],
            [
                InlineKeyboardButton(text=BACK_BUTTON, callback_data=seller_callback.new(
                    action=f'product_{product.id}', shop=str(shop.id)
                ))
            ]
        ]
    )
    return keyboard


def get_seller_shop_delete_keyboard(shop: Shop):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=DELETE_BUTTON, callback_data=seller_callback.new(
                    action='delete_confirm', shop=str(shop.id)
                ))
            ],
            [
                InlineKeyboardButton(text=BACK_BUTTON, callback_data=seller_callback.new(
                    action='main', shop=str(shop.id)
                ))
            ]
        ]
    )
    return keyboard


def get_seller_shop_info_keyboard(shop: Shop):
    inline_keyboard = [
        [
            InlineKeyboardButton(text=EDIT_NAME_BUTTON, callback_data=seller_callback.new(
                action='change_shop_name', shop=str(shop.id)
            )),
            InlineKeyboardButton(text=EDIT_DESCRIPTION_BUTTON, callback_data=seller_callback.new(
                action='change_shop_description', shop=str(shop.id)
            )),
            InlineKeyboardButton(text=EDIT_PHOTO_BUTTON, callback_data=seller_callback.new(
                action='change_shop_photo', shop=str(shop.id)
            )),
        ],
        [
            InlineKeyboardButton(text=DELETE_BUTTON, callback_data=seller_callback.new(
                action='delete', shop=str(shop.id)
            ))
        ],
        [
            InlineKeyboardButton(text=BACK_BUTTON, callback_data=seller_callback.new(
                action='main', shop=''
            ))
        ]
    ]

    if shop.catalog:
        inline_keyboard.insert(0, [
            InlineKeyboardButton(text=CATEGORIES_BUTTON, callback_data=seller_callback.new(
                action='categories', shop=str(shop.id)
            )),
        ])
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard


async def get_seller_product_info_keyboard(product: Product, shop: Shop):
    inline_keyboard = [
        [
            InlineKeyboardButton(text=EDIT_NAME_BUTTON, callback_data=seller_callback.new(
                action=f'name_product_{product.id}', shop=str(shop.id)
            )),
            InlineKeyboardButton(text=EDIT_DESCRIPTION_BUTTON, callback_data=seller_callback.new(
                action=f'description_product_{product.id}', shop=str(shop.id)
            )),
        ],
        [
            InlineKeyboardButton(text=EDIT_PRICE_BUTTON, callback_data=seller_callback.new(
                action=f'price_product_{product.id}', shop=str(shop.id)
            )),
            InlineKeyboardButton(text=EDIT_PHOTO_BUTTON, callback_data=seller_callback.new(
                action=f'photo_product_{product.id}', shop=str(shop.id)
            )),
        ],
        [
            InlineKeyboardButton(text=DELETE_BUTTON, callback_data=seller_callback.new(
                action=f'delete_product_{product.id}', shop=str(shop.id)
            ))
        ],
        [
            InlineKeyboardButton(text=BACK_BUTTON, callback_data=seller_callback.new(
                action=f'shop_cat_{(await product.category).id}', shop=str(shop.id)
            ))
        ]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
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


async def get_seller_products_keyboard(shop: Shop, category: CategoryShop):
    products = await category.products.filter(active=True)
    inline_keyboard = []
    for product in products:
        inline_keyboard.append(
            [
                InlineKeyboardButton(text=product.name, callback_data=seller_callback.new(
                    action=f'product_{product.id}', shop=str(shop.id)),
                )
            ]
        )

    if len(products) < 99:
        inline_keyboard.append(
            [InlineKeyboardButton(text=ADD_PRODUCT_BUTTON, callback_data=seller_callback.new(
                action=f'new_product_{category.id}', shop=str(shop.id)
            ))]
        )

    inline_keyboard.append(
        [
            InlineKeyboardButton(text=BACK_BUTTON, callback_data=seller_callback.new(
                action=f'shop_cat_{category.id}', shop=str(shop.id)
            ))
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard


async def get_seller_categories_keyboard(shop_id):
    categories = await Category.all()
    inline_keyboard = []

    for i in range(0, len(categories), 2):
        if i != len(categories) - 1:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(text=categories[i].name, callback_data=seller_callback.new(
                        action=f'select_cat_{categories[i].id}', shop=str(shop_id)
                    )),
                    InlineKeyboardButton(text=categories[i + 1].name, callback_data=seller_callback.new(
                        action=f'select_cat_{categories[i + 1].id}', shop=str(shop_id)
                    )),
                ]
            )
        else:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(text=categories[i].name, callback_data=seller_callback.new(
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


async def get_seller_shop_categories_keyboard(shop: Shop):
    categories = await shop.categories
    inline_keyboard = []

    for i in range(0, len(categories), 2):
        if i != len(categories) - 1:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(text=categories[i].name, callback_data=seller_callback.new(
                        action=f'shop_cat_{categories[i].id}', shop=str(shop.id)
                    )),
                    InlineKeyboardButton(text=categories[i + 1].name, callback_data=seller_callback.new(
                        action=f'shop_cat_{categories[i + 1].id}', shop=str(shop.id)
                    )),
                ]
            )
        else:
            inline_keyboard.append(
                [
                    InlineKeyboardButton(text=categories[i].name, callback_data=seller_callback.new(
                        action=f'shop_cat_{categories[i].id}', shop=str(shop.id)
                    ))
                ]
            )

    if len(categories) < 100:
        inline_keyboard.append(
            [
                InlineKeyboardButton(text=ADD_CATEGORY_BUTTON, callback_data=seller_callback.new(
                    action='add_cat', shop=str(shop.id)
                ))
            ]
        )

    inline_keyboard.append(
        [
            InlineKeyboardButton(text=BACK_BUTTON, callback_data=seller_callback.new(
                action='info', shop=str(shop.id)
            ))
        ]
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard
