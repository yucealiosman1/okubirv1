# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, DateTime, SmallInteger, ForeignKeyConstraint, Table, Unicode
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import association_proxy
from flask_security import RoleMixin, UserMixin

from okubir import db

class Status:
    recommended, will_read, reading, have_read, removed = range(5)
    names = ['Tavsiye edilenler', 'Okunacaklar', u'Şu anda okuduklarım', u'Okunmuşlar', u'Silinmiş']

roles_users = db.Table(
        'roles_users',
        Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)
interest_book = db.Table(
        'interest_book',
        Column('interest_id', db.Integer(), db.ForeignKey('interest_area.id')),
        Column('category_id', db.Integer(), db.ForeignKey('book_category.id'))
)
interests_users = db.Table(
        'interests_users',
        Column('interest_id', db.Integer(), db.ForeignKey('interest_area.id')),
        Column('user_id', db.Integer(), db.ForeignKey('user.id'))
)
categories_books = db.Table(
        'categories_books',
        Column('category_id', db.Integer(), db.ForeignKey('book_category.id')),
        Column('book_id', db.Integer(), db.ForeignKey('book.id'))
)
    
class Role(db.Model, RoleMixin):
    id = Column(Integer(), primary_key=True)
    name = Column(String(32), unique=True)
    description = Column(String(255))

    def __unicode__(self):
        return self.name
    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)

class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True)
    password = Column(String(255))
    name = Column(String(64))
    surname = Column(String(64))
    last_login = Column(DateTime())
    active = Column(Boolean())
    confirmed_at = Column(DateTime())
    confirmed = Column(Boolean)
    birth_date = Column(Date)
    #country = Column(String(32))
    il_id = Column(Integer, ForeignKey('iller.id'))
    ilce_id = Column(Integer, ForeignKey('ilceler.id'))
    semt_id = Column(Integer, ForeignKey('semtler.id'))
    reading_goal_id = Column(Integer, ForeignKey('reading_goal.id'))
    reading_goal = relationship("ReadingGoal", back_populates="user")
    book_assocs = relationship("UserBook", back_populates="user")
    books = association_proxy('book_assocs', 'book')
    summaries = association_proxy('book_assocs', 'summary')
    comments = relationship('Comment', back_populates="user")
    interests = relationship('InterestArea', secondary=interests_users, back_populates="users")
    roles = relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))
    il = relationship("Il", uselist=False)
    ilce = relationship("Ilce", uselist=False)
    semt = relationship("Semt", uselist=False)

    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymous(self):
        return False
    def get_name(self):
        return self.name + ' ' + self.surname
    def __repr__ (self):
        return self.get_name()

class Book(db.Model):
    __tablename__ = "book"
    id = Column(Integer, primary_key=True)
    name = Column(String(128))
    author_id = Column(Integer, ForeignKey('author.id'))
    publication_place = Column(String(128))
    publication_year = Column(Integer)
    publisher_id = Column(Integer, ForeignKey('publisher.id'))
    isbn = Column(String(13))
    page_amount = Column(Integer, nullable=False)
    ebook_fname = Column(String(64))
    image_fname = Column(String(64))
    like_amount = Column(Integer, default=0)
    score_amount = Column(Integer, default=0)
    description = Column(String(1500))
    
    comments = relationship("Comment", back_populates="book")
    author = relationship("Author", back_populates="books")
    publisher = relationship("Publisher", back_populates="books")
    user_assocs = relationship("UserBook", back_populates="book")
    summaries = association_proxy('user_assocs', 'summary')
    categories = relationship('BookCategory', secondary=categories_books, back_populates="books")
    
    def __repr__ (self):
        return self.name + " " + "(%s)" % self.author.get_name()

class UserBook(db.Model):
    __tablename__ = 'userbook'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    book_id = Column(Integer, ForeignKey('book.id'), nullable=False)
    summary_id = Column(Integer, ForeignKey('summary.id'))
    status = Column(Integer)
    pages_read = Column(Integer)
    user = relationship("User", back_populates="book_assocs")
    book = relationship("Book", back_populates="user_assocs")
    summary = relationship("Summary", back_populates="userbook")
    notes = relationship("Note", back_populates="userbook")
    logs = relationship("UserBookLog", back_populates="userbook")
    rating = Column(Integer, default=0)
    
    def __init__(self, user, book, status, pages_read=0):
        self.user = user
        self.book = book
        self.status = status
        self.pages_read = pages_read
    
    def get_status_name(self):
        return Status.names[self.status]
    
    def __repr__ (self):
        return self.user.get_name() + " - " + self.book.name + "(" + Status.names[self.status] + ")"

class UserBookLog(db.Model):
    __tablename__ = 'userbooklogs'
    id = Column(Integer, primary_key=True)
    userbook_id = Column(Integer, ForeignKey('userbook.id'), nullable=False)
    time = Column(DateTime, nullable=False)
    starting_page = Column(SmallInteger, nullable=False)
    ending_page = Column(SmallInteger, nullable=False)
    old_status = Column(SmallInteger)
    new_status = Column(SmallInteger, nullable=False)
    userbook = relationship("UserBook", back_populates="logs")
    user = association_proxy('userbook', 'user')
    book = association_proxy('userbook', 'book')
    
class Author(db.Model):
    __tablename__ = "author"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    surname = Column(String(64), nullable=False)
    books = relationship("Book", back_populates="author")
    
    def get_name(self):
        return self.name + ' ' + self.surname
    
    def __repr__ (self):
        return self.get_name()

class Publisher(db.Model):
    __tablename__ = "publisher"
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    books = relationship("Book", back_populates="publisher")
    
    def __repr__ (self):
        return self.name

class InterestArea(db.Model):
    __tablename__ = 'interest_area'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    categories = relationship('BookCategory', secondary=interest_book, back_populates='interests')
    users = relationship('User', secondary=interests_users, back_populates="interests")
    
    def __repr__ (self):
        return self.name

class BookCategory(db.Model):
    __tablename__ = "book_category"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    interests = relationship('InterestArea', secondary=interest_book, back_populates='categories')
    books = relationship('Book', secondary=categories_books, back_populates="categories")
    
    def __repr__ (self):
        return self.name

class Note(db.Model):
    __tablename__ = "note"
    id = Column(Integer, primary_key=True)
    userbook_id = Column(Integer, ForeignKey('userbook.id'))
    time_created = Column(DateTime, nullable=False)
    time_last_modified = Column(DateTime)
    is_public = Column(Boolean)
    text = Column(String(500))
    userbook = relationship("UserBook", back_populates="notes")
    user = association_proxy('userbook', 'user')
    book = association_proxy('userbook', 'book')
    page = Column(Integer)

class Comment(db.Model):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    text = Column(String(500), nullable=False)
    time_created = Column(DateTime, nullable=False)
    time_last_modified = Column(DateTime)
    book_id = Column(Integer, ForeignKey('book.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    book = relationship("Book", back_populates="comments")
    user = relationship('User', back_populates="comments")
    
class Summary(db.Model):
    __tablename__ = "summary"
    id = Column(Integer, primary_key=True)
    text = Column(String(5000), nullable=False)
    time_created = Column(DateTime, nullable=False)
    time_last_modified = Column(DateTime)
    userbook = relationship("UserBook", back_populates="summary", uselist=False)
    user = association_proxy('userbook', 'user')
    book = association_proxy('userbook', 'book')

class ReadingGoal(db.Model):
    __tablename__ = "reading_goal"
    id = Column(Integer, primary_key=True)
    goal = Column(Integer)
    pages_read_today = Column(Integer)
    last_update = Column(DateTime())
    reached = Column(Boolean)
    user = relationship("User", back_populates="reading_goal", uselist=False)
    
    def __repr__ (self):
        if self.user:
            return "User id: %s goal: %s" % (self.user.id, self.goal)
        else:
            return "No user. goal: %s"% (self.goal)


class Il(db.Model):
    __tablename__ = 'iller'
    id = Column(Integer, primary_key=True)
    ad = Column(Unicode(255), nullable=False)
    sef = Column(String(255), nullable=False)
    ilces = relationship("Ilce", back_populates="il", primaryjoin='Il.id == Ilce.il_id')
    semts = relationship("Semt", back_populates="il")
    def __repr__(self):
        return self.sef

class Ilce(db.Model):
    __tablename__ = 'ilceler'
    id = Column(Integer, primary_key=True)
    il_id = Column(Integer, ForeignKey('iller.id'), nullable=False)
    ad = Column(Unicode(255), nullable=False)
    sef = Column(String(255), nullable=False)
    il = relationship("Il", back_populates="ilces", primaryjoin='Ilce.il_id == Il.id')
    semts = relationship("Semt", back_populates="ilce")
    def __repr__(self):
        return self.sef

class Semt(db.Model):
    __tablename__ = 'semtler'
    id = Column(Integer, primary_key=True)
    il_id = Column(Integer, ForeignKey('iller.id'), nullable=False)
    ilce_id = Column(Integer, ForeignKey('ilceler.id'), nullable=False)
    ad = Column(Unicode(255), nullable=False)
    sef = Column(String(255), nullable=False)
    il = relationship("Il", back_populates="semts", primaryjoin='Semt.il_id == Il.id')
    ilce = relationship("Ilce", back_populates="semts", primaryjoin='Semt.ilce_id == Ilce.id')
    def __repr__(self):
        return self.sef
