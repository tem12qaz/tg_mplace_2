from flask import redirect, url_for, request
from flask_security import current_user

from flask_admin import BaseView, AdminIndexView, expose

from flask_admin.contrib.sqla import ModelView


class AdminMixin:
    def is_accessible(self):
        return current_user.has_role('admin')

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('security.login', next=request.url))


class HomeAdminView(AdminMixin, AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin_home.html')


class CategoryView(AdminMixin, ModelView):
    column_list = ('id', 'name', 'channel')

    form_columns = ('name', 'channel')


class ShopView(AdminMixin, ModelView):
    column_list = ('id', 'name', 'description', 'category')

    form_columns = ('id', 'name', 'description', 'category')


class ServiceView(AdminMixin, ModelView):
    column_list = ('id', 'name', 'description', 'photo', 'service_category', 'field1', 'field2', 'field3', 'field4', 'field5')

    form_columns = ('name', 'description', 'photo', 'service_category', 'field1', 'field2', 'field3', 'field4', 'field5')


class LogoutView(AdminMixin, BaseView):
    @expose('/')
    def logout_button(self):
        return redirect(url_for('security.logout', next='/admin'))
