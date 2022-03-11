import os
import os.path as op
import time

from flask import redirect, url_for, request
from flask_admin.form import FileUploadField, ImageUploadField
from flask_security import current_user

from flask_admin import BaseView, AdminIndexView, expose, form

from flask_admin.contrib.sqla import ModelView
from jinja2 import Markup
from werkzeug.utils import secure_filename
from wtforms import ValidationError

basedir = os.path.abspath(os.path.dirname(__file__))
file_path = os.path.join(basedir, 'files')


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


def name_gen(obj, file_data):
    parts = op.splitext(file_data.filename)
    return secure_filename(f'file-{time.time()}%s%s' % parts)


class ServiceView(AdminMixin, ModelView):
    column_list = (
    'id', 'name', 'description', 'photo', 'service_category', 'field1', 'field2', 'field3', 'field4', 'field5')

    form_columns = (
    'name', 'description', 'photo', 'service_category', 'field1', 'field2', 'field3', 'field4', 'field5')

    # d
    def picture_validation(form, field):
        if field.data:
            filename = field.data.filename
            if filename[-4:] != '.jpg' and filename[-4:] != '.png':
                raise ValidationError('file must be .jpg or .png')
        data = field.data.stream.read()
        field.data = data
        return True

    # @staticmethod
    def picture_formatter(view, context, model, name):
        return '' if not getattr(model, name) else 'a picture'

    # column_formatters = dict(photo=picture_formatter)
    # form_overrides = dict(photo=FileUploadField)
    # form_args = dict(photo=dict(validators=[picture_validation]))

    def _list_thumbnail(view, context, model, name):
        if not model.photo:
            return ''

        return Markup(
            '<img src="%s">' %
            url_for('static',
                    filename=form.thumbgen_filename(model.photo))
        )

    column_formatters = {
        'photo': _list_thumbnail
    }

    form_extra_fields = {
        'photo': ImageUploadField(
            'photo', base_path=file_path, thumbnail_size=(100, 100, True))
    }


class LogoutView(AdminMixin, BaseView):
    @expose('/')
    def logout_button(self):
        return redirect(url_for('security.logout', next='/admin'))
