from typing import Any

import pytest
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test.client import Client
from django.urls.base import reverse
from ulid import ULID

from example.models import Item
from ulid_django.forms import ULIDField

ulid = ULID()
ulid_str = str(ulid)
ulid_hex = ulid.hex

invalid_values = [
    "Z" * 32,
    "0" * 30,
    "?" * 26,
]


class TestULIDField:
    @pytest.fixture
    def ulid_field(self) -> ULIDField:
        return ULIDField()

    @pytest.mark.parametrize(
        "value, expected",
        [
            (None, None),
            (ulid_str, ulid_str),
            (ulid, ulid_str),
        ],
    )
    def test_prepare_value(
        self,
        ulid_field: ULIDField,
        value: Any,
        expected: str | None,
    ) -> None:
        assert ulid_field.prepare_value(value) == expected

    @pytest.mark.parametrize(
        "value, expected",
        [
            (None, None),
            ("", None),
            (ulid, ulid),
            (ulid_str, ulid),
            (ulid_hex, ulid),
        ],
    )
    def test_to_python(
        self,
        ulid_field: ULIDField,
        value: Any,
        expected: ULID | None,
    ) -> None:
        assert ulid_field.to_python(value) == expected

    @pytest.mark.parametrize("value", invalid_values)
    def test_to_python_invalid(self, ulid_field: ULIDField, value: Any) -> None:
        with pytest.raises(ValidationError) as exc_info:
            ulid_field.to_python(value)
        assert exc_info.value.code == "invalid"
        assert "ULID" in exc_info.value.message


@pytest.mark.django_db
class TestIntegration:
    @pytest.fixture
    def admin(self) -> User:
        return User.objects.create_superuser(username="admin")

    @pytest.fixture
    def admin_client(self, client: Client, admin: User) -> Client:
        client.force_login(admin)
        return client

    @pytest.fixture
    def item(self) -> Item:
        return Item.objects.create(name="item", etag=ulid)

    @pytest.mark.parametrize("value", [ulid_str, ulid_hex])
    def test_form_get_set(self, admin_client: Client, item: Item, value: str) -> None:
        Item.objects.filter(pk=item.pk).update(etag=None)

        url = reverse("admin:example_item_change", args=[item.pk])

        response = admin_client.get(url)
        assert response.status_code == 200
        soup = BeautifulSoup(response.content, "lxml")
        etag_field = soup.find("input", {"name": "etag"})
        assert etag_field.get("value") is None  # type: ignore[union-attr]

        form_data = {
            "name": item.name,
            "etag": value,
            "_save": "Save",
        }
        response = admin_client.post(url, form_data, follow=True)
        assert response.status_code == 200

        response = admin_client.get(url)
        assert response.status_code == 200
        soup = BeautifulSoup(response.content, "lxml")
        etag_field = soup.find("input", {"name": "etag"})
        assert etag_field.get("value") == ulid_str  # type: ignore[union-attr]

    @pytest.mark.parametrize("value", invalid_values)
    def test_form_set_invalid(
        self,
        admin_client: Client,
        item: Item,
        value: str,
    ) -> None:
        url = reverse("admin:example_item_change", args=[item.pk])

        form_data = {
            "name": item.name,
            "etag": value,
            "_save": "Save",
        }
        response = admin_client.post(url, form_data, follow=True)
        soup = BeautifulSoup(response.content, "lxml")
        etag_error_list = soup.find("ul", class_="errorlist")
        assert "ULID" in etag_error_list.text  # type: ignore[union-attr]
