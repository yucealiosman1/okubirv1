import unittest
import os
from flask_security import utils

from okubir import app, db, user_datastore
from okubir.models import User, Book, Author, Publisher
from okubir.config import TestConfig

from datetime import datetime

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        app.config.from_object(TestConfig)
        self.app = app.test_client()
        self.init_database()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def init_database(self):
        db.create_all()
        encrypted_password = utils.encrypt_password('password')
        user_datastore.create_user(email='user@example.com', password=encrypted_password, name="Userguy", surname="Userson")
        user_datastore.create_user(email='editor@example.com', password=encrypted_password, name="Editorman", surname="Editson")
        user_datastore.create_user(email='admin@example.com', password=encrypted_password, name="Admin", surname="Adminson")
        user_datastore.find_or_create_role(name='admin', description='Administrator')
        user_datastore.find_or_create_role(name='user', description='User')
        user_datastore.find_or_create_role(name='editor', description='Editor')
        tolstoy = Author(id=1, name="L.", surname="Tolstoy")
        tolkien = Author(id=2, name="J.R.R", surname="Tolkien")
        rowling = Author(id=3, name="J.K.", surname="Rowling")
        bloomsbury = Publisher(name="Bloomsbury")
        db.session.add(tolstoy)
        db.session.add(tolkien)
        db.session.add(rowling)
        db.session.add(bloomsbury)
        db.session.commit()
        user_datastore.add_role_to_user('user@example.com', 'user')
        user_datastore.add_role_to_user('editor@example.com', 'editor')
        user_datastore.add_role_to_user('admin@example.com', 'admin')
        db.session.add(Book(name="War and Peace", author=tolstoy, page_amount=1225))
        db.session.add(Book(name="Hobbit", author=tolkien, page_amount=300))
        db.session.add(Book(name="Harry Potter and the Philosopher's Stone", author=rowling, publisher=bloomsbury, publication_year=1997, publication_place="UK", isbn="0-7475-3269-9", page_amount=223))
        db.session.add(Book(name="Harry Potter and the Chamber of Secrets", author=rowling, publisher=bloomsbury, publication_year=1998, publication_place="UK", isbn="0-7475-3849-2", page_amount=251))
        db.session.commit()
