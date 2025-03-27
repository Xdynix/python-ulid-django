from django.db import models
from ulid import ULID

from ulid_django.models import ULIDField


class Item(models.Model):
    name = models.CharField(max_length=100, blank=True)
    etag = ULIDField(default=ULID, blank=True, null=True)

    class Meta:
        indexes = (models.Index(fields=["etag"]),)

    def __str__(self) -> str:
        return f"Item: {self.name or '(blank)'}"
