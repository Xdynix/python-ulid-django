from django.contrib import admin

from example.models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin[Item]):
    pass
