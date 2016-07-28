# -*- coding: utf-8 -*-
# tests/test_books.py

import unittest
from flask_login import current_user
from flask import request, url_for

from base import BaseTestCase
from okubir.dao import getObject, findUserBook
from okubir.models import *
from okubir.views.general_views import format_time

class TestBook(BaseTestCase):
    
# User can add a book to list
    def test_add_book_to_user(self):
        with self.app:
            self.app.post(
                '/login',
                data=dict(email="user@example.com", password="password"),
                follow_redirects=True
            )
            response = self.app.get(
                '/add_book_to_user?book_id=1&status=1',
                follow_redirects=True
            )
            book = getObject(1, Book)
            self.assertIn(book, current_user.books)
            self.assertEqual(response.status_code, 200)
    
    # User can remove a book from list
    def test_remove_book_from_user(self):
        with self.app:
            self.app.post(
                '/login',
                data=dict(email="user@example.com", password="password"),
                follow_redirects=True
            )
            self.app.get(
                '/add_book_to_user?book_id=1&status=1',
                follow_redirects=True
            )
            book = getObject(1, Book)
            self.assertIn(book, current_user.books)
            response = self.app.get(
                '/remove_book_list?book_id=1',
                follow_redirects=True
            )
            #self.assertNotIn(book, current_user.books)
            assoc = findUserBook(current_user.id, 1)
            self.assertEqual(assoc.status, Status.removed)
            self.assertEqual(response.status_code, 200)

    # User can update a book in list
    def test_update_book_in_user(self):
        with self.app:
            self.app.post(
                '/login',
                data=dict(email="user@example.com", password="password"),
                follow_redirects=True
            )
            self.app.get(
                '/add_book_to_user?book_id=1&status=1',
                follow_redirects=True
            )
            book = getObject(1, Book)
            self.assertIn(book, current_user.books)
            response = self.app.get(
                '/update_book_list?book_id=1&status=2',
                follow_redirects=True
            )
            assoc = findUserBook(current_user.id, 1)
            self.assertEqual(assoc.status, 2)
            self.assertEqual(response.status_code, 200)
            
    # User can crud a summary
    def test_summary(self):
        with self.app:
            self.app.post(
                '/login',
                data=dict(email="user@example.com", password="password"),
                follow_redirects=True
            )
            self.app.get(
                '/add_book_to_user?book_id=1&status=3',
                follow_redirects=True
            )
            book = getObject(1, Book)
            self.assertIn(book, current_user.books)
            # create
            response = self.app.post(
                '/write_summary/1',
                data=dict(summary="Summary summary summary"),
                follow_redirects=True
            )
            assoc = findUserBook(current_user.id, 1)
            self.assertIn("Özet yazıldı", response.data)
            self.assertIsNotNone(assoc.summary)
            self.assertEqual("Summary summary summary", assoc.summary.text)
            # read
            response = self.app.get(
                '/summary/1',
                follow_redirects=True
            )
            self.assertIn("Summary summary summary", response.data)
            self.assertIn("Özetleyen - Userguy Userson", response.data)
            # update
            response = self.app.post(
                '/edit_summary/1',
                data=dict(summary="Hede hodo hudu"),
                follow_redirects=True
            )
            self.assertIn("Özet güncellendi!", response.data)
            self.assertIn("Hede hodo hudu", response.data)
            self.assertIn(format_time(assoc.summary.time_last_modified), response.data)
            self.assertEqual("Hede hodo hudu", assoc.summary.text)
            # delete
            response = self.app.get(
                '/delete_summary/1',
                follow_redirects=True
            )
            self.assertIn("Özet silindi!", response.data)
            self.assertNotIn("Hede hodo hudu", response.data)
            self.assertIsNone(assoc.summary)

    # User can crd a note
    def test_note(self):
        with self.app:
            self.app.post(
                '/login',
                data=dict(email="user@example.com", password="password"),
                follow_redirects=True
            )
            self.app.get(
                '/add_book_to_user?book_id=1&status=2',
                follow_redirects=True
            )
            book = getObject(1, Book)
            self.assertIn(book, current_user.books)
            # create
            response = self.app.post(
                '/write_note/1',
                data=dict(page=10, note="Note note note"),
                follow_redirects=True
            )
            assoc = findUserBook(current_user.id, 1)
            self.assertIn("Not yazıldı!", response.data)
            self.assertIsNotNone(assoc.notes)
            self.assertNotEqual(assoc.notes, [])
            self.assertEqual("Note note note", assoc.notes[0].text)
            self.assertEqual(10, assoc.notes[0].page)
            self.assertFalse(assoc.notes[0].is_public)
            # read note in the user page
            response = self.app.get(
                '/userpage',
                follow_redirects=True
            )
            self.assertIn("Note note note", response.data)
            self.assertIn(format_time(assoc.notes[0].time_created), response.data)
            # delete
            response = self.app.get(
                '/remove_note/1',
                follow_redirects=True
            )
            self.assertIn("Not silindi!", response.data)
            self.assertNotIn("Note note note", response.data)
            self.assertEqual(assoc.notes, [])
    
    # User can crud a comment
    def test_comment(self):
        with self.app:
            self.app.post(
                '/login',
                data=dict(email="user@example.com", password="password"),
                follow_redirects=True
            )
            self.app.get(
                '/add_book_to_user?book_id=1&status=3',
                follow_redirects=True
            )
            book = getObject(1, Book)
            self.assertIn(book, current_user.books)
            # create
            response = self.app.post(
                '/write_comment/1',
                data=dict(comment="Comment comment comment"),
                follow_redirects=True
            )
            self.assertIn("Yorum yazıldı!", response.data)
            self.assertIsNotNone(book.comments)
            self.assertNotEqual(book.comments, [])
            self.assertEqual("Comment comment comment", book.comments[0].text)
            # read
            response = self.app.get(
                '/bookread/1',
                follow_redirects=True
            )
            self.assertIn("Comment comment comment", response.data)
            self.assertIn(format_time(book.comments[0].time_created), response.data)
            response = self.app.get(
                '/book/1',
                follow_redirects=True
            )
            self.assertIn("Comment comment comment", response.data)
            self.assertIn(format_time(book.comments[0].time_created), response.data)
            # update
            response = self.app.post(
                '/edit_comment/1',
                data=dict(comment="Hede hodo hudu"),
                follow_redirects=True
            )
            self.assertIn("Yorum düzenlendi!", response.data)
            self.assertIn("Hede hodo hudu", response.data)
            self.assertIn(format_time(book.comments[0].time_last_modified), response.data)
            self.assertEqual("Hede hodo hudu", book.comments[0].text)
            # delete
            response = self.app.get(
                '/remove_comment/1',
                follow_redirects=True
            )
            self.assertIn("Yorum silindi!", response.data)
            self.assertNotIn("Hede hodo hudu", response.data)
            self.assertEqual(book.comments, [])
            self.assertEqual(current_user.comments, [])
    
    # User can rate a book
    def test_rate(self):
        with self.app:
            self.app.post(
                '/login',
                data=dict(email="user@example.com", password="password"),
                follow_redirects=True
            )
            self.app.get(
                '/add_book_to_user?book_id=1&status=3',
                follow_redirects=True
            )
            book = getObject(1, Book)
            assoc = findUserBook(current_user.id, 1)
            self.assertIn(book, current_user.books)
            self.assertEqual(book.like_amount, 0)
            self.assertEqual(book.score_amount, 0)
            self.assertEqual(assoc.rating, 0)
            # 0 -> 1
            self.app.get(
                '/ratebook/1?rate=1'
            )
            self.assertEqual(book.like_amount, 1)
            self.assertEqual(book.score_amount, 1)
            self.assertEqual(assoc.rating, 1)
            # 1 -> 0
            self.app.get(
                '/ratebook/1?rate=1'
            )
            self.assertEqual(book.like_amount, 0)
            self.assertEqual(book.score_amount, 0)
            self.assertEqual(assoc.rating, 0)
            # 0 -> -1
            self.app.get(
                '/ratebook/1?rate=-1'
            )
            self.assertEqual(book.like_amount, 0)
            self.assertEqual(book.score_amount, 1)
            self.assertEqual(assoc.rating, -1)
            # -1 -> 0
            self.app.get(
                '/ratebook/1?rate=-1'
            )
            self.assertEqual(book.like_amount, 0)
            self.assertEqual(book.score_amount, 0)
            self.assertEqual(assoc.rating, 0)
            # -1 -> 1
            self.app.get(
                '/ratebook/1?rate=-1'
            )
            self.app.get(
                '/ratebook/1?rate=1'
            )
            self.assertEqual(book.like_amount, 1)
            self.assertEqual(book.score_amount, 1)
            self.assertEqual(assoc.rating, 1)
            # 1 -> -1
            self.app.get(
                '/ratebook/1?rate=-1'
            )
            self.assertEqual(book.like_amount, 0)
            self.assertEqual(book.score_amount, 1)
            self.assertEqual(assoc.rating, -1)
            
if __name__ == '__main__':
    unittest.main()
