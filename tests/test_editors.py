# tests/test_editors.py

import unittest

from flask_login import current_user
from flask import request, url_for

from base import BaseTestCase
from okubir.dao import getObject
from okubir.models import *

class TestEditor(BaseTestCase):
    
    # Editor login works
    def test_correct_login_editor(self):
        with self.app:
            response = self.app.post(
                '/login',
                data=dict(email="editor@example.com", password="password"),
                follow_redirects=True
            )
            self.assertIn(b'/', response.data)
            self.assertIn(b'Sisteme Kitap Ekle', response.data)
            self.assertTrue(current_user.email == "editor@example.com")
            self.assertTrue(current_user.is_active)

    # Editor can add books
    def test_add_book(self):
        with self.app:
            self.app.post(
                '/login',
                data=dict(email="editor@example.com", password="password"),
                follow_redirects=True
            )
            response = self.app.post(
                '/add_book',
                data=dict(name="New Book", author="1", publication_place="Hedede", publication_year="1950", publisher="1", page_amount="500"),
                follow_redirects=True
            )
            self.assertIn(b'Kitap eklendi.', response.data)
            book = getObject(5, Book)
            self.assertEqual("New Book", book.name)
            self.assertEqual("Tolstoy", book.author.surname)
            self.assertEqual("Hedede", book.publication_place)
            self.assertEqual(1950, book.publication_year)
            self.assertEqual("Bloomsbury", book.publisher.name)
            self.assertEqual(500, book.page_amount)
            

