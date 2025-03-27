from django.urls import path, register_converter

from ulid_django.converters import ULIDConverter

from . import views

register_converter(ULIDConverter, "ulid")

urlpatterns = [
    path("dummy/<ulid:item_id>/", views.dummy_view, name="dummy_view"),
]
