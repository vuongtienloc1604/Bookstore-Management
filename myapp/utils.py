
from myapp import app, db
from myapp.model import Book, BookAuthor, User, Publisher, BookCategory, UserRole, Receipt, ReceiptDetail, Comment, \
    BookImportingForm, OfflineReceipt, OfflineReceiptDetail, Author
from flask_login import current_user
from sqlalchemy import func, DateTime
from sqlalchemy.sql import extract
import hashlib


def load_book_category():
    return BookCategory.query.all()


def load_publisher():
    return Publisher.query.all()


def load_author():
    return Author.query.all()


def load_book_all():
    return Book.query.all()


def load_books(book_cate_id, book_name=None, pub_id=None, kw=None, from_price=None, to_price=None, page=1):
    books = Book.query.filter(Book.active.__eq__(True))

    if book_name:
        books = books.filter(Book.name.contains(book_name))

    if book_cate_id:
        books = books.filter(Book.book_category_id.__eq__(book_cate_id))

    if pub_id:
        books = books.filter(Book.publisher_id.__eq__(pub_id))

    if kw:
        books = books.filter(Book.name.contains(kw))

    if from_price:
        books = books.filter(Book.price.__ge__(from_price))

    if to_price:
        books = books.filter(Book.price.__le__(to_price))

    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size

    return books.slice(start, start + page_size).all()


def count_books():
    return Book.query.filter(Book.active.__eq__(True)).count()


def add_user(name, username, password, **kwargs):
    password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
    user = User(name=name.strip(), username=username.strip(), password=password, email=kwargs.get('email'),
                avatar=kwargs.get('avatar'))
    db.session.add(user)
    try:
        db.session.commit()
    except:
        return False
    else:
        return True


def check_login(username, password, role=UserRole.USER):
    if username and password:
        password = str(hashlib.md5(password.strip().encode('utf-8')).hexdigest())
        return User.query.filter(User.username.__eq__(username.strip()),
                                 User.password.__eq__(password),
                                 User.user_role.__eq__(role)).first()


def get_user_by_name(user_name):
    return User.query.get(user_name)


def get_user_by_id(user_id):
    return User.query.get(user_id)


def get_book_by_id(book_id):
    return Book.query.get(book_id)


def category_stats():
    return db.session.query(BookCategory.id, BookCategory.name, func.count(Book.id))\
                     .join(Book, BookCategory.id.__eq__(Book.book_category_id), isouter=True)\
                     .group_by(BookCategory.id, BookCategory.name).all()


def add_receipt(cart):
    if cart:
        receipt = Receipt(user=current_user)
        db.session.add(receipt)
        try:
            for c in cart.values():
                d = ReceiptDetail(receipt=receipt,
                                  book_id=c['id'],
                                  quantity=c['quantity'],
                                  unit_price=c['price'])
                db.session.add(d)
                db.session.commit()
        except:
            return {'status': 404, 'err_msg': 'Chuong trinh dang bi loi'}


def add_offline_receipt(form):
    if form:
        offline_receipt = OfflineReceipt(user=current_user)
        db.session.add(offline_receipt)
        try:
            for b in form.values():
                i = OfflineReceiptDetail(offline_receipt=offline_receipt,
                                         book_id=b['id'],
                                         quantity=b['quantity'],
                                         unit_price=b['price'],
                                         customer_name=b['customer_name'])
                db.session.add(i)
                db.session.commit()
        except:
            return {'status': 404, 'err_msg': 'Chuong trinh dang bi loi'}

# def add_book_form(form):
#     if form:
#         bform = BookImportingForm(user=current_user)
#         db.session.add(bform)
#
#         for b in form.values():
#             d = Book(bform=bform,
#                               book_name=b['name'],
#                               book_cate_id = b['book_cate.name'],
#                               author_id = c['author_id'],
#                               quantity=c['quantity'])
#             db.session.add(d)
#         db.session.commit()


def count_cart(cart):
    total_quantity, total_amount = 0, 0

    if cart:
        for c in cart.values():
            total_quantity += c['quantity']
            total_amount += c['quantity'] * c['price']

    return {
        'total_quantity': total_quantity,
        'total_amount': total_amount
    }


def count_item_saleform(form):
    total_quantity, total_amount = 0, 0

    if form:
        for i in form.values():
            total_quantity += i['quantity']
            total_amount += i['quantity'] * i['price']

    return {
        'total_quantity': total_quantity,
        'total_amount': total_amount
    }

def book_stats(kw=None, from_date=None, to_date=None):
    q = db.session.query(Book.id, Book.name, func.sum(ReceiptDetail.quantity*ReceiptDetail.unit_price))\
                  .join(ReceiptDetail, ReceiptDetail.book_id.__eq__(Book.id), isouter=True)\
                  .join(Receipt, ReceiptDetail.receipt_id.__eq__(Receipt.id))

    if kw:
        q = q.filter(Book.name.contains(kw))

    if from_date:
        q = q.filter(Receipt.created_date.__ge__(from_date))

    if to_date:
        q = q.filter(Receipt.created_date.__le__(to_date))

    return q.group_by(Book.id, Book.name).all()


def book_month_stats(year):
    q = db.session.query(extract('month', Receipt.created_date),
                         func.sum(ReceiptDetail.quantity * ReceiptDetail.unit_price)) \
        .join(Receipt, ReceiptDetail.receipt_id.__eq__(Receipt.id))\
        .filter(extract('year', Receipt.created_date).__eq__(year))

    return q.group_by(extract('month', Receipt.created_date)).all()


def add_comment(content, book_id):
    c = Comment(content=content, book_id=book_id, user=current_user)
    db.session.add(c)
    db.session.commit()
    return c


def get_comment(book_id, page=1):
    page_size = app.config['COMMENT_SIZE']
    start = (page - 1) * page_size
    return Comment.query.filter(Comment.book_id.__eq__(book_id)).order_by(-Comment.id).slice(start,
                                                                                             start + page_size).all()


def count_commnent(book_id):
    return Comment.query.filter(Comment.book_id.__eq__(book_id)).count()


def add_book(name, image, type, publish_date, price, in_stock, book_category_id, publisher_id):
    b = Book(name=name, image=image, type=type, publish_date=publish_date, price=price,in_stock=in_stock, book_category_id=book_category_id,
             publisher_id=publisher_id)
    db.session.add(b)
    db.session.commit()
    return b

def update_json():
    try:
        db.session.commit()
        return True
    except Exception as ex:
        print(ex)
        return False


def update_book(book_id, name, image, type, publish_date, price, in_stock, book_category_id, publisher_id):
    b = get_book_by_id(book_id)
    b.name = name
    b.image = image
    b.type = type
    b.publish_date = publish_date
    b.price = price
    b.in_stock = in_stock
    b.book_category_id = book_category_id
    b.publisher_id = publisher_id
    db.session.add(b)
    db.session.commit()
    return b


def delete_book(book_id):
    b = get_book_by_id(book_id)
    db.session.delete(b)
    db.session.commit()


def add_book_cate(name):
    cat = BookCategory(name=name)
    db.session.add(cat)
    db.session.commit()
    return cat
#
#
# def delete_comment(book_id):
#     c = Comment.query.filter(Comment.book_id == int(book_id))
#     db.session.delete(c)
#     db.session.commit()
#
#
# def delete_receipt_detail(book_id):
#     r = ReceiptDetail.query.filter(ReceiptDetail.book_id == int(book_id))
#     db.session.delete(r)
#     db.session.commit()