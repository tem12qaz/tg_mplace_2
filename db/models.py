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


class Form(Model):
    id = fields.IntField(pk=True)
    shop = fields.OneToOneField('models.Shop', related_name='form', index=True, null=True)
    field1 = fields.CharField(256)
    field2 = fields.CharField(256, null=True)
    field3 = fields.CharField(256, null=True)
    field4 = fields.CharField(256, null=True)
    field5 = fields.CharField(256, null=True)

    def fields(self):
        return self.field1, self.field2, self.field3, self.field4, self.field5


class Bid(Model):
    id = fields.IntField(pk=True)
    form = fields.ForeignKeyField('models.Form', related_name='bids', null=True)
    field1 = fields.CharField(1024)
    field2 = fields.CharField(1024, null=True)
    field3 = fields.CharField(1024, null=True)
    field4 = fields.CharField(1024, null=True)
    field5 = fields.CharField(1024, null=True)

    def fields(self):
        return self.field1, self.field2, self.field3, self.field4, self.field5


class Photo(Model):
    id = fields.IntField(pk=True)
    source = fields.BinaryField()
    product = fields.ForeignKeyField('models.Product', related_name='photos', index=True, null=True)


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
    channel = fields.CharField(32, null=True)


class Service(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(100)
    description = fields.TextField()
    photo = fields.TextField()
    service_category = fields.ForeignKeyField('models.ServiceCategory', related_name='services', index=True)
    field1 = fields.CharField(1024, null=True)
    field2 = fields.CharField(1024, null=True)
    field3 = fields.CharField(1024, null=True)
    field4 = fields.CharField(1024, null=True)
    field5 = fields.CharField(1024, null=True)

    def fields(self):
        return self.field1, self.field2, self.field3, self.field4, self.field5


class ServiceCategory(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(100)
    channel = fields.CharField(32, null=True)


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
