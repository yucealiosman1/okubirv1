# -*- coding: utf-8 -*-
import os
from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, utils
from flask_uploads import UploadSet, configure_uploads, IMAGES
from flask_admin import Admin
from flask_babelex import Babel

import config

app = Flask(__name__)
app.config.from_object(os.environ['APP_CONFIG'])
app.jinja_env.add_extension('jinja2.ext.loopcontrols')

db = SQLAlchemy(app)

ebooks = UploadSet('ebooks', ('pdf',))
book_images = UploadSet('bookimages', IMAGES)

configure_uploads(app, (ebooks, book_images))

babel = Babel(app)

from models import *
import views
from views.admin_views import *
from forms import UserLoginForm

admin = Admin(app, name='okubir', template_mode='bootstrap3', base_template='admin/base_mod.html')
admin.add_view(UserView(User, db.session, u"Kullanıcılar"))
admin.add_view(BookView(Book, db.session, u"Kitaplar"))
admin.add_view(AuthorView(Author, db.session, u"Yazarlar"))
admin.add_view(PublisherView(Publisher, db.session, u"Yayınevleri"))
admin.add_view(SummaryView(Summary, db.session, u"Özetler"))
admin.add_view(CommonView(InterestArea, db.session, u"İlgi alanları"))
admin.add_view(CommonView(BookCategory, db.session, u"Kategoriler"))
admin.add_view(LogView(UserBookLog, db.session, u"Loglar"))

user_datastore = SQLAlchemyUserDatastore(db, models.User, models.Role)
security = Security(app, user_datastore, login_form=UserLoginForm)

def get_text(key):
    #print key
    if key == "Please log in to access this page.":
        return u"Bu sayfaya erişmek için giriş yapmalısınız."

@babel.localeselector
def get_locale():
    return 'tr'
        
app.login_manager.localize_callback = get_text

@app.before_first_request
def createDB():
    db.create_all()
    if not user_datastore.get_user('user@example.com'):
        user_datastore.create_user(email='user@example.com', password=utils.encrypt_password('password'), name="Userguy", surname="Userson", confirmed=True)
    if not user_datastore.get_user('editor@example.com'):
        user_datastore.create_user(email='editor@example.com', password=utils.encrypt_password('password'), name="Editorman", surname="Editson", confirmed=True)
    if not user_datastore.get_user('admin@example.com'):
        user_datastore.create_user(email='admin@example.com', password=utils.encrypt_password('password'), name="Admin", surname="Adminson", confirmed=True)
    user_datastore.find_or_create_role(name='admin', description='Administrator')
    user_datastore.find_or_create_role(name='user', description='User')
    user_datastore.find_or_create_role(name='editor', description='Editor')
    db.session.commit()
    user_datastore.add_role_to_user('user@example.com', 'user')
    user_datastore.add_role_to_user('editor@example.com', 'editor')
    user_datastore.add_role_to_user('admin@example.com', 'admin')
    db.session.commit()
    
