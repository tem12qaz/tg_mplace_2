from flask_security import UserMixin, RoleMixin

from flask_app_init import db

roles_users = db.Table('roles_users',
                       db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
                       db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
                       )


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100), unique=True)
    description = db.Column(db.String(255))


class Category(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    channel = db.Column(db.String(32), nullable=True)
    shops = db.relationship('Shop', backref='category', lazy=True)

    def __repr__(self):
        return 'id' + str(self.id) + ' ' + self.name


class ServiceCategory(db.Model):
    __tablename__ = 'servicecategory'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    channel = db.Column(db.String(32), nullable=True)


class Shop(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.Text())
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)


