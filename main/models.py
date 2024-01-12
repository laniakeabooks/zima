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
    contact = models.CharField(max_length=300)
    resource = models.URLField()

    class Meta:
        verbose_name_plural = "Entries"
