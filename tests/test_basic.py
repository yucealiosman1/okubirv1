# tests/test_basic.py

import unittest
from urlparse import urlparse

from base import BaseTestCase


class FlaskTestCase(BaseTestCase):

    # Flask was set up correctly
    def test_works(self):
        response = self.app.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
