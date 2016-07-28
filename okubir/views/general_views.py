# -*- coding: utf-8 -*-
from flask import Flask, flash, redirect, session, request, render_template, url_for, send_from_directory
from flask_login import login_required, current_user, login_user
from flask_security import logout_user, LoginForm, utils
from okubir import app, db, book_images, ebooks
from okubir.models import *
from okubir.forms import WriteCommentForm
from okubir import dao

def format_time(time):
    return time.strftime('%H:%M %d/%m/%Y')

def make_news(logs):
    news_list = []
    for log in logs:
        news = ""
        if log.user.ilce:
            if log.user.ilce_id == current_user.ilce_id:
                if log.user.semt:
                    news += log.user.semt.ad + u" semtinden bir okur, "
                else:
                    news += log.user.ilce.ad + u" ilçesinden bir okur, "
            else:
                if log.user.il_id == current_user.il_id:
                    news += log.user.ilce.ad + u" ilçesinden bir okur, "
                else:
                    news += log.user.il.ad + u" ilinden bir okur, "
        elif log.user.il:
            news += log.user.il.ad + u" ilinden bir okur, "
        else:
            news += u"Bir okur, "
        
        news += '<a href="/book/%s">%s</a> ' % (log.book.id, log.book)
        if log.ending_page > log.starting_page:
            news += u"isimli kitaptan %s sayfa okudu. " % (log.ending_page - log.starting_page)
            if log.new_status == Status.have_read:
                news += u"Kitabı bitirdi. "
        elif log.new_status != log.old_status:
            news += u"isimli kitabı "
            if log.new_status == Status.have_read:
                news += u"bitirdi."
            elif log.new_status == Status.reading:
                news += u"okumaya başladı."
            elif log.new_status == Status.will_read:
                news += u"okunacaklar listesine ekledi."
        news_list.append((log.time, news))
    return news_list
            

@app.context_processor
def inject_status():
    return dict(status=Status)

@app.context_processor
def inject_format_time():
    return dict(format_time=format_time)
    
@app.context_processor
def inject_functions():
    return dict(image_path=book_images.url, ebook_path=ebooks.url)


@app.route('/about')
def about():
    return redirect('/')
    
@app.route('/contact')
def contact():
    return redirect('/')
    
@app.route('/', methods=['POST', 'GET'])
@login_required
def home():
    #logs = UserBookLog.query.join(UserBookLog.userbook, aliased=True).filter(UserBook.user_id!=current_user.id).order_by(UserBookLog.time.desc()).limit(10).all()
    logs = UserBookLog.query.order_by(UserBookLog.time.desc()).limit(10).all()
    news_list = make_news(logs)
    return render_template("home.html", news=news_list)

@app.route('/summary/<int:sum_id>')
def summaryPage(sum_id):
    summary = dao.getObject(sum_id, Summary)
    if summary is None:
        flash(u'Özet bulunmuyor', 'warning')
        return redirect(request.referrer or '/')
    return render_template('summary_page.html', summary=summary)

@app.route('/book/<int:book_id>')
@login_required
def bookPage(book_id):
    book = dao.getObject(book_id, Book)
    if book is None:
        flash('Kitap bulunmuyor', 'warning')
        return redirect(request.referrer or '/')
    assoc = dao.findUserBook(current_user.id, book_id)
    return render_template('book_page.html', book=book, assoc=assoc, comment_form=WriteCommentForm())
    
@app.route('/search_book/<int:page>')
@app.route('/search_book')
#@login_required
def searchBook(page=1):
    keywords = request.args.get("words").split()
    books = dao.findBooks(keywords).paginate(page, 5, False)
    return render_template('search_page.html', books=books, words=request.args.get("words"))

# adds example objects
@app.route('/initdb')
def initDB():
    tolstoy = Author(name="L.", surname="Tolstoy")
    tolkien = Author(name="J.R.R", surname="Tolkien")
    rowling = Author(name="J.K.", surname="Rowling")
    bloomsbury = Publisher(name="Bloomsbury")
    db.session.add(tolstoy)
    db.session.add(tolkien)
    db.session.add(rowling)
    db.session.add(bloomsbury)
    db.session.commit()
    db.session.add(Book(name="War and Peace", author=tolstoy, page_amount=1225, image_fname="warandpeace.jpg"))
    db.session.add(Book(name="Hobbit", author=tolkien, page_amount=300, image_fname="hobbit.jpg"))
    db.session.add(Book(name="Harry Potter and the Philosopher's Stone", author=rowling, publisher=bloomsbury, publication_year=1997, publication_place="UK", isbn="0-7475-3269-9", page_amount=223, image_fname="philosopher.jpg"))
    db.session.add(Book(name="Harry Potter and the Chamber of Secrets", author=rowling, publisher=bloomsbury, publication_year=1998, publication_place="UK", isbn="0-7475-3849-2", page_amount=251, image_fname="chamber.jpg"))
    db.session.commit()
    return redirect(url_for('index'))
