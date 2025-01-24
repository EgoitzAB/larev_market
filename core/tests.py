# core/tests.py
from django.test import TestCase
from django.urls import reverse
from http import HTTPStatus

class RobotsTxtTests(TestCase):
    def test_get(self):
        response = self.client.get(reverse('robots_txt'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response['Content-Type'], 'text/plain')