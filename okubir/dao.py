from okubir import db
from models import *
from datetime import datetime

def commit():
    db.session.commit()
    
def addObject(obj):
    db.session.add(obj)

def deleteObject(obj):
    db.session.delete(obj)

def getObject(id, _class):
    obj = None
    try:
        obj = db.session.query(_class).get(int(id))
    finally:
        return obj

def findUserBook(user_id, book_id):
    return UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()

def getBooks():
    return Book.query.all()
    
def getIlces(il_id):
    return Ilce.query.filter_by(il_id=il_id).all()
    
def getSemts(ilce_id):
    return Semt.query.filter_by(ilce_id=ilce_id).all()

def findBooks(keywords):
    patterns = [Book.name.like('%'+k+'%') for k in keywords]
    return Book.query.filter(db.and_(*patterns)).order_by(Book.name)

def associateBookWithUser(book_id, user_id, status):
    book = Book.query.get(book_id)
    user = User.query.get(user_id)
    if book in user.books:
        return False
    assoc = UserBook(user, book, status)
    db.session.add(assoc)
    log = UserBookLog(
                time = datetime.now(),
                starting_page = 0,
                ending_page = 0,
                old_status = None,
                new_status = status,
                userbook = assoc
            )
    db.session.add(log)
    return True

def removeBookFromUser(book_id, user_id):
    updateAssocStatus(book_id, user_id, None, Status.removed)
    """
    assoc = UserBook.query.filter_by(book_id=book_id, user_id=user_id).first()
    for note in assoc.notes:
        db.session.delete(note)
    if assoc.summary:
        db.session.delete(assoc.summary)
    db.session.delete(assoc)
    """
    
def updatePagesRead(assoc, new_pages_read, old_pages_read):
    page = int(new_pages_read)
    if page <= assoc.book.page_amount:
        assoc.pages_read = page
        if assoc.user.reading_goal:
            assoc.user.reading_goal.pages_read_today += page - old_pages_read
        if page == assoc.book.page_amount:
            return Status.have_read;
    return None
    
def updateAssocStatus(book_id, user_id, new_pages_read = None, new_status = None):
    assoc = UserBook.query.filter_by(book_id=book_id, user_id=user_id).first()
    if new_status == Status.removed:
        assoc.pages_read = 0
        assoc.status = Status.removed
        return False
    old_pages_read = assoc.pages_read
    old_status = assoc.status
    if new_pages_read is not None:
        new_status = updatePagesRead(assoc, new_pages_read, old_pages_read)
    if new_status is not None:
        new_status = int(new_status)
        assoc.status = new_status
    log = UserBookLog(
                time = datetime.now(),
                starting_page = old_pages_read,
                ending_page = new_pages_read or old_pages_read,
                old_status = old_status,
                new_status = new_status or old_status,
                userbook = assoc
            )
    db.session.add(log)
    return new_status == Status.have_read
