# -*- coding: utf-8 -*-
# tests/test_users.py

import unittest

from flask_login import current_user
from flask import request, url_for

from base import BaseTestCase

class TestUser(BaseTestCase):

    # Normal user login works
    def test_correct_login_normal(self):
        with self.app:
            response = self.app.post(
                '/login',
                data=dict(email="user@example.com", password="password"),
                follow_redirects=True
            )
            self.assertIn(b'Kullanıcı Sayfası', response.data)
            self.assertNotIn(b'Yeni Kitap Ekle', response.data)
            self.assertTrue(current_user.email == "user@example.com")
            self.assertTrue(current_user.is_active)

    # Admin login works
    def test_correct_login_admin(self):
        with self.app:
            response = self.app.post(
                '/login',
                data=dict(email="admin@example.com", password="password"),
                follow_redirects=True
            )
            self.assertIn(b'Sisteme Kitap Ekle', response.data)
            self.assertTrue(current_user.email == "admin@example.com")
            self.assertTrue(current_user.is_active)
            self.assertIn('admin', current_user.roles)

    # Login behaves correctly with incorrect credentials
    def test_incorrect_login(self):
        response = self.app.post(
            '/login',
            data=dict(email="wrong", password="credentials"),
            follow_redirects=True
        )
        self.assertIn(b'Giriş yap', response.data)
        self.assertIn(b'Specified user does not exist', response.data)
        self.assertFalse(current_user.is_active)
    
    # User can register
    def test_user_registeration(self):
        with self.app:
            response = self.app.post(url_for('registerUser'), data=dict(
                name='User', surname='Userson', email='user@hede.com', password='password', confirm='password',
                birth_date='01/01/1901', il=0
            ), follow_redirects=True)
            self.assertIsNotNone(current_user)
            self.assertTrue(current_user.is_active)
            self.assertEqual(current_user.email, "user@hede.com")
            #self.assertEqual(current_user.birth_date, )
            self.assertIsNotNone(current_user.last_login)

    # Invalid user registration
    def test_invalid_user_registeration(self):
        with self.app:
            response = self.app.post(url_for('registerUser'), data=dict(
                name='User432', surname='Use!rson', birth_date='01-02-1990',
                email='not_an_email', password='pass', confirm='different'
            ), follow_redirects=True)
            self.assertIn(b'İsim sadece harflerden oluşmalıdır.', response.data)
            self.assertIn(b'Soyisim sadece harflerden oluşmalıdır.', response.data)
            self.assertIn(b'Doğum tarihi verilen formatta olmalıdır', response.data)
            self.assertIn(b'Hatalı e-posta adresi', response.data)
            self.assertIn(b'Parolalar eşleşmeli', response.data)
            self.assertIn(b'Parola 6 ila 25 karakter uzunluğunda olmalıdır', response.data)
            self.assertIn(b'/register', request.url)

	# Logout works
    def test_logout(self):
        with self.app:
            self.app.post(
                '/login',
                data=dict(email="user@example.com", password="password"),
                follow_redirects=True
            )
            response = self.app.get('/logout', follow_redirects=True)
            self.assertIn(b'Giriş yap', response.data)
            self.assertFalse(current_user.is_active)

    # Logout page requires user login
    def test_logout_requires_login(self):
        with self.app:
            response = self.app.get(url_for('logout'), follow_redirects=True)
            self.assertIn(b'Bu sayfaya erişmek için giriş yapmalısınız.', response.data)

    
if __name__ == '__main__':
    unittest.main()
