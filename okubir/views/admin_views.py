# -*- coding: utf-8 -*-
from flask_admin.contrib.sqla import ModelView
from flask_admin.actions import action
from flask_admin import expose
from flask_login import current_user, login_required
from wtforms import PasswordField
from flask_security import utils
from okubir.models import *
from okubir import app, dao
from okubir.forms import RecommendBookForm
from flask import redirect, url_for, render_template, request, session, flash
from datetime import date

class CommonView(ModelView):
    #create_modal = True
    #edit_modal = True
    
    def is_accessible(self):
        return current_user.has_role('admin')

@app.route('/recommend_book', methods=['POST', 'GET'])
@login_required
def recommendBook():
    if 'admin' not in current_user.roles or not session['ids_list']:
        flash(u'Bu sayfaya erişim izniniz yok.', 'warning')
        return redirect(url_for('index'))
    form = RecommendBookForm(request.form)
    if form.validate_on_submit():
        ids = session['ids_list']
        for user_id in ids:
            dao.associateBookWithUser(form.book.data, user_id, Status.recommended)
        dao.commit()
        #session['ids_list'] = None
        flash(u'Kitap önerme tamamlandı.', 'info')
    return render_template('recommend_book.html', form=form)

class UserView(CommonView):
    column_exclude_list = ['password',]
    form_excluded_columns = ['password','book_assocs', 'reading_goal', 'comments', 'last_login', 'active']
    column_searchable_list = ['name', 'surname']
    column_editable_list = ['confirmed']
    column_list = ['email', 'name', 'surname', 'last_login', 'confirmed_at', 'confirmed', 'birth_date', 'age', 'il', 'ilce', 'semt','interests']
    column_labels = dict(email="E-posta adresi", name=u"İsim", surname=u"Soyisim", last_login=u"Son giriş tarihi", confirmed_at=u"Doğrulandığı zaman",
                            confirmed=u"Doğrulanmış", birth_date=u"Doğum Tarihi", age=u'Yaş', il=u"İl", ilce=u"İlçe", semt="Semt", interests=u"İlgi Alanları", roles="Roller")
    column_filters = ['interests', 'semt', 'ilce']
    column_default_sort = ('birth_date', True)
    #column_sortable_list = ['age']
    
    
    def _age_formatter(view, context, model, name):
        today = date.today()
        born = model.birth_date
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        
    column_formatters = {
       'age': _age_formatter
    }
    
    @action('recommend', u'Kitap öner', 'Bu kullanicilara kitap onermek istediginize emin misiniz?')
    def action_approve(self, ids):
        #users = User.query.filter(User.id.in_(ids)).all()
        session['ids_list'] = ids
        return redirect(url_for('recommendBook'))
            
    def scaffold_form(self):
        form_class = super(UserView, self).scaffold_form()
        form_class.password2 = PasswordField('Yeni parola')
        return form_class
    
    def on_model_change(self, form, model, is_created):
        if hasattr(model, 'password2') and len(model.password2):
            model.password = utils.encrypt_password(model.password2)

class BookView(CommonView):
    form_excluded_columns = ['user_assocs']
    column_list = ['read_amount', 'name', 'author', 'publisher', 'publication_place', 'publication_year', 'isbn', 'page_amount', 'ebook_fname', 'categories']
    column_labels = dict(publisher=u"Yayınevi", author=u"Yazar", name=u"İsim", publication_place=u"Yayın yeri", publication_year=u"Yayın yılı", isbn=u"ISBN",
        page_amount=u"Sayfa Sayısı", ebook_fname=u"E-kitap Dosya Adı", categories=u"Kategori", read_amount=u"Okur sayısı")
    column_descriptions = dict(read_amount=u"Kitabı okumakta veya okumuş olan kişi sayısı")
                            
    def _read_amount_formatter(view, context, model, name):
        readers = [x for x in model.user_assocs if x.status == Status.reading or x.status == Status.have_read]
        return len(readers)
    column_formatters = {
       'read_amount': _read_amount_formatter
    }

    
class PublisherView(CommonView):
    column_list = ['name', 'books']
    column_labels = dict(name=u"İsim", books=u"Kitaplar")
    form_excluded_columns = ['books']
    
class SummaryView(CommonView):
    column_list = ['book', 'user']
    column_labels = dict(book="Kitap", user=u"Kullanıcı")
    column_searchable_list = ['userbook.book.name', 'userbook.user.name']

class AuthorView(CommonView):
    column_list = ['name', 'surname', 'books']
    column_labels = dict(name=u"İsim", surname="Soyisim", books=u"Kitaplar")
    form_excluded_columns = ['books']

class LogView(CommonView):
    column_labels = dict(userbook=u"Kullanıcı-Kitap ilişkisi", time=u"Zaman", starting_page=u"Başlangıç sayfası", ending_page=u"Bitiş sayfası", old_status=u"Eski durum", new_status=u"Yeni durum")
    
    def _status_formatter(view, context, model, name):
        value = getattr(model, name)
        return Status.names[value] if value else ""
        
    column_formatters = {
       'old_status': _status_formatter,
       'new_status': _status_formatter
    }
