from datetime import datetime, timedelta
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main import models


class IndexTest(TestCase):
    def test_get(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)


class SubmitTest(TestCase):
    def test_entry(self):
        data = {
            "email": "email@example.com",
            "contact": "email@example.com",
            "resource": "https://example.com",
        }
        response = self.client.post(reverse("index"), data)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("submit_success"), response.url)
        self.assertTrue(models.Entry.objects.filter(email=data["email"]).exists())
        self.assertTrue(models.Entry.objects.filter(contact=data["contact"]).exists())
        self.assertTrue(models.Entry.objects.filter(resource=data["resource"]).exists())
        self.assertEqual(models.Entry.objects.all().count(), 1)


class MatchTest(TestCase):
    def setUp(self):
        now = timezone.now()
        three_days_ago = now - timedelta(days=3)
        with patch.object(timezone, "now", return_value=three_days_ago):
            self.p1 = models.Entry.objects.create(
                contact="p1@example.com",
                resource="http://example.com/article/100",
            )
            self.p2 = models.Entry.objects.create(
                contact="p2@elsewhere.com",
                resource="http://example.com/article/100",
            )

    def test_match(self):
        output = StringIO()
        call_command("match", stdout=output)
        now = timezone.now()
        self.assertTrue(
            models.Matching.objects.filter(
                person_who_received=self.p1,
                person_who_was_received=self.p2,
                created_at__date=now.date(),
            ).exists()
        )


class MatchEarlyTest(TestCase):
    def setUp(self):
        now = timezone.now()
        one_day_ago = now - timedelta(days=1)
        with patch.object(timezone, "now", return_value=one_day_ago):
            self.p1 = models.Entry.objects.create(
                contact="p1@example.com",
                resource="http://example.com/article/100",
            )
            self.p2 = models.Entry.objects.create(
                contact="p2@elsewhere.com",
                resource="http://example.com/article/100",
            )

    def test_no_match(self):
        output = StringIO()
        call_command("match", stdout=output)
        self.assertEqual(models.Matching.objects.all().count(), 0)
