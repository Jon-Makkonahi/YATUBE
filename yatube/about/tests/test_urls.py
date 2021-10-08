# posts/tests/tests_url.py
from django.test import TestCase, Client

URL_AUTHOR = '/about/author/'
URL_TECH = '/about/tech/'


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_about(self):
        url_pages = [
            [URL_AUTHOR, self.guest_client, 200],
            [URL_TECH, self.guest_client, 200],
        ]
        for page in url_pages:
            with self.subTest(page=page):
                response = page[1].get(page[0])
                self.assertEqual(response.status_code, page[2])
