from myapp import app, db
from flask_admin import Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from myapp.model import Book, Author, Publisher, BookCategory, UserRole, User
from flask_login import current_user, logout_user
from flask import redirect, request
import utils
from datetime import datetime


class AuthenticatedModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role.__eq__(UserRole.ADMIN)


class BookView(AuthenticatedModelView):
    can_view_details = True
    can_edit = True
    can_export = True
    column_searchable_list = ['name', 'type']
    column_filters = ['name', 'price']
    column_exclude_list = ['image', 'active', 'publish_date']
    column_labels = {
        'name': 'Ten SP',
        'book_category_id': 'Danh muc',
        'price': 'Gia',
        'image': 'Anh dai dien',
        'type': 'The loai'
    }
    column_sortable_list = ['id', 'name', 'price']
    form_excluded_columns = ['author_details', 'receipt_details', 'comments', 'offline_receipt_details',
                             'book_importing_form']


class AuthorView(AuthenticatedModelView):
    can_view_details = True
    can_edit = True
    can_export = True
    form_excluded_columns = ['releases']


class PublisherView(AuthenticatedModelView):
    can_view_details = True
    form_excluded_columns = ['books']


class BookCategoryView(AuthenticatedModelView):
    can_view_details = True
    form_excluded_columns = ['books']


class UserView(AuthenticatedModelView):
    can_view_details = True
    form_excluded_columns = ['receipts', 'comments']


class LogoutView(BaseView):
    @expose('/')
    def __index__(self):
        logout_user()
        return redirect('/admin')

    def is_accessible(self):
        return current_user.is_authenticated


class MyAdminIndex(AdminIndexView):
    @expose('/')
    def __index__(self):
        return self.render('admin/index.html', stats=utils.category_stats())


class StatsView(BaseView):
    @expose('/')
    def index(self):
        kw = request.args.get('kw')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        year = request.args.get('year', datetime.now().year)

        return self.render('admin/stats.html',
                           month_stats=utils.book_month_stats(year=year),
                           stats=utils.book_stats(kw=kw,
                                                  from_date=from_date,
                                                  to_date=to_date))

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.ADMIN


admin = Admin(app=app, name="Login Administration", template_mode='bootstrap4', index_view=MyAdminIndex())
admin.add_view(BookView(Book, db.session))
admin.add_view(AuthorView(Author, db.session))
admin.add_view(PublisherView(Publisher, db.session))
admin.add_view(BookCategoryView(BookCategory, db.session))
admin.add_view(UserView(User, db.session))
admin.add_view(StatsView(name='Stats'))
admin.add_view(LogoutView(name='Logout'))
