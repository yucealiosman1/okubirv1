# -*- coding: utf-8 -*-
from flask import Flask, flash, redirect, request, render_template, url_for, send_from_directory
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from okubir import app, ebooks, book_images
from okubir.forms import BookAddForm
from okubir.models import *
from okubir import dao
import os

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/add_book', methods=['POST', 'GET'])
@login_required
def addBook():
    if 'editor' not in current_user.roles and 'admin' not in current_user.roles:
        flash(u'Bu sayfaya erişim izniniz yok.', 'warning')
        return redirect(url_for('index'))
    form = BookAddForm(request.form)
    if form.validate_on_submit():
        author = dao.getObject(form.author.data, Author)
        
        publisher = None
        ebook_fname = None
        image_fname = None
        if form.publisher.data:
            publisher = dao.getObject(form.publisher.data, Publisher)
        if form.ebook.data:
            ebook_fname = ebooks.save(request.files[form.ebook.name])
        if form.image.data:
            image_fname = book_images.save(request.files[form.image.name])
        book = Book(
                name = form.name.data,
                author = author,
                publication_place= form.publication_place.data,
                publication_year= form.publication_year.data,
                publisher = publisher,
                isbn = form.isbn.data,
                page_amount = form.page_amount.data,
                description = form.description.data,
                ebook_fname = ebook_fname,
                image_fname = image_fname
        )
        dao.addObject(book)
        dao.commit();
        flash('Kitap eklendi.', 'info')
        return redirect(url_for('index'))
    return render_template('add_book.html', form=form)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)
