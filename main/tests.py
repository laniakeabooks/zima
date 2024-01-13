from django.test import TestCase
from django.urls import reverse

from main import models


class IndexTest(TestCase):
    def test_get(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)


class SubmitTest(TestCase):
    def test_entry(self):
        data = {
            "contact": "email@example.com",
            "resource": "https://example.com",
        }
        response = self.client.post(reverse("index"), data)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("submit_success"), response.url)
        self.assertTrue(models.Entry.objects.filter(contact=data["contact"]).exists())
        self.assertTrue(models.Entry.objects.filter(resource=data["resource"]).exists())
        self.assertEqual(models.Entry.objects.all().count(), 1)
