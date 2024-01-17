import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    first_name = None
    last_name = None
    email = models.EmailField(
        blank=True,
        null=True,
        unique=True,
    )


class Entry(models.Model):
    verify_key = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    terms = models.BooleanField(default=False)
    email = models.EmailField()
    contact = models.CharField(max_length=300)
    resource = models.URLField()
    has_received = models.ManyToManyField("Entry", through="Matching")
    is_verified = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        ret = f"[{self.id}]"
        if len(self.contact) > 20:
            ret += f"({self.contact[:20]}...)"
        else:
            ret += f"({self.contact})"
        if len(self.resource) > 25:
            ret += f"({self.resource[:25]}...)"
        return ret

    class Meta:
        verbose_name_plural = "Entries"


class Matching(models.Model):
    person_who_received = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
        related_name="informed_entry",
    )
    person_who_was_received = models.ForeignKey(
        Entry,
        on_delete=models.CASCADE,
        related_name="content_entry",
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Matchlog(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    receiver = models.ForeignKey(Entry, on_delete=models.CASCADE)
