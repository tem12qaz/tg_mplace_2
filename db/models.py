from tortoise.models import Model
from tortoise import fields
from flask_security import UserMixin, RoleMixin


class TelegramUser(Model):
    id = fields.IntField(pk=True)
    telegram_id = fields.BigIntField(unique=True, index=True)
    username = fields.CharField(128, unique=True, null=True)
    state = fields.CharField(64, default='')

    def __str__(self):
        return str(self.telegram_id)


class Shop(Model):
    id = fields.IntField(pk=True)
    active = fields.BooleanField(default=False, index=True)
    owner = fields.ForeignKeyField('models.TelegramUser', related_name='shops', index=True)
    category = fields.ForeignKeyField('models.Category', related_name='shops', index=True, null=True)
    name = fields.CharField(100)
    description = fields.TextField()
    photo = fields.BinaryField(null=True)
    catalog = fields.BooleanField(default=False, index=True)


class Product(Model):
    id = fields.IntField(pk=True)
    price = fields.IntField()
    active = fields.BooleanField(default=False)
    category = fields.ForeignKeyField('models.CategoryShop', related_name='products', index=True)
    name = fields.CharField(100)
    description = fields.TextField()


class Photo(Model):
    id = fields.IntField(pk=True)
    source = fields.BinaryField()
    product = fields.ForeignKeyField('models.Product', related_name='photos', index=True)


class Deal(Model):
    id = fields.IntField(pk=True)
    shop = fields.ForeignKeyField('models.Shop', related_name='deals', index=True)
    customer = fields.ForeignKeyField('models.TelegramUser', related_name='deals', index=True)
    price = fields.IntField()
    state = fields.CharField(32)


class Review(Model):
    id = fields.IntField(pk=True)
    product = fields.ForeignKeyField('models.Product', related_name='reviews', index=True)
    shop = fields.ForeignKeyField('models.Shop', related_name='reviews', index=True)
    customer = fields.ForeignKeyField('models.TelegramUser', related_name='reviews', index=True)
    text = fields.TextField()
    rating = fields.SmallIntField()


class Category(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(100)


class ServiceCategory(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(100)


class CategoryShop(Model):
    id = fields.IntField(pk=True)
    shop = fields.ForeignKeyField('models.Shop', related_name='categories', index=True)
    name = fields.CharField(100)


class User(Model, UserMixin):
    id = fields.IntField(pk=True)
    email = fields.CharField(254, unique=True)
    password = fields.CharField(255)
    active = fields.BooleanField()
    roles = fields.ManyToManyField(
        'models.Role', related_name='users', through='roles_users'
    )


class Role(Model, RoleMixin):
    id = fields.IntField(pk=True)
    name = fields.CharField(100, unique=True)
    description = fields.CharField(255)
