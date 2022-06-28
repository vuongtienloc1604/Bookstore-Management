from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Enum
from myapp import db
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as UserEnum
from flask_login import UserMixin


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class UserRole(UserEnum):
    ADMIN = 1
    MANAGER = 2
    STORE_MANAGER = 3
    BOOK_SELLER = 4
    USER = 5


class User(BaseModel, UserMixin):
    name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(50), nullable=False)
    avatar = Column(String(100))
    active = Column(Boolean, default=True)
    email = Column(String(100))
    #phone = Column(String(15))
    joined_date = Column(DateTime, default=datetime.now())
    user_role = Column(Enum(UserRole), default=UserRole.USER)
    receipts = relationship('Receipt', backref='user', lazy=True)
    comments = relationship('Comment', backref='user', lazy=True)

    def str(self):
        return self.name


class BookCategory(BaseModel):
    __tablename__ = 'book_category'
    name = Column(String(30), nullable=False)
    books = relationship('Book', backref='BookCategory', lazy=False)

    def __str__(self):
        return self.name


class Publisher(BaseModel):
    __tablename__ = 'publisher'
    name = Column(String(50), nullable=False)
    books = relationship('Book', backref='publisher', lazy=False)

    def __str__(self):
        return self.name


class Author(BaseModel):
    __tablename__ = 'author'
    name = Column(String(50), nullable=False)
    releases = relationship('BookAuthor', backref='author', lazy=True)

    def str(self):
        return self.name


class Book(BaseModel):
    __tablename__ = 'book'
    name = Column(String(50), nullable=False)
    image = Column(String(100))
    type = Column(String(50), nullable=False)
    publish_date = Column(DateTime, default=datetime.now())
    price = Column(Float, nullable=False)
    active = Column(Boolean, default=True)
    in_stock = Column(Integer)
    min_input_required = Column(Integer, default=int(150))
    min_in_stock_required = Column(Integer, default=int(300))
    publisher_id = Column(Integer, ForeignKey(Publisher.id), nullable=False)
    book_category_id = Column(Integer, ForeignKey(BookCategory.id), nullable=False)
    author_details = relationship('BookAuthor', backref='book', lazy=True)
    receipt_details = relationship('ReceiptDetail', backref='book', lazy=True)
    comments = relationship('Comment', backref='book', lazy=True)
    offline_receipt_details = relationship('OfflineReceiptDetail', backref='book', lazy=True)
    book_importing_form = relationship('BookImportingFormDetail', backref='book', lazy=True)

    def str(self):
        return self.name


class BookAuthor(db.Model):
    author_id = Column(Integer, ForeignKey(Author.id), nullable=False, primary_key=True)
    book_id = Column(Integer, ForeignKey(Book.id), nullable=False, primary_key=True)


class Receipt(BaseModel):
    created_date = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    details = relationship('ReceiptDetail', backref='receipt', lazy=True)


class OfflineReceipt(BaseModel):
    created_date = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    details = relationship('OfflineReceiptDetail', backref='offline_receipt', lazy=True)


class ReceiptDetail(db.Model):
    receipt_id = Column(Integer, ForeignKey(Receipt.id), nullable=False, primary_key=True)
    book_id = Column(Integer, ForeignKey(Book.id), nullable=False, primary_key=True)
    quantity = Column(Integer, default=0)
    unit_price = Column(Float, default=0)
    expired_date = Column(DateTime, default=datetime.now())


class OfflineReceiptDetail(db.Model):
    receipt_id = Column(Integer, ForeignKey(OfflineReceipt.id), nullable=False, primary_key=True)
    book_id = Column(Integer, ForeignKey(Book.id), nullable=False, primary_key=True)
    customer_name = Column(String(50), nullable=False)
    quantity = Column(Integer, default=0)
    unit_price = Column(Float, default=0)


class Comment(BaseModel):
    content = Column(String(255), nullable=False)
    book_id = Column(Integer, ForeignKey(Book.id), nullable=False)
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    created_date = Column(DateTime, default=datetime.now())

    def __str__(self):
        return self.content


class BookImportingForm(BaseModel):
    created_date = Column(DateTime, default=datetime.now())
    user_id = Column(Integer, ForeignKey(User.id), nullable=False)
    details = relationship('BookImportingFormDetail', backref='bform', lazy=True)


class BookImportingFormDetail(db.Model):
    book_importing_form_id = Column(Integer, ForeignKey(BookImportingForm.id), nullable=False, primary_key=True)
    book_id = Column(Integer, ForeignKey(Book.id), nullable=False, primary_key=True)
    book_cate_id = Column(Integer, ForeignKey(BookCategory.id), nullable=False)
    author_id = Column(Integer, ForeignKey(Author.id), nullable=False)
    quantity = Column(Integer, default=0)


if __name__ == '__main__':
    db.create_all()
