from http import HTTPStatus
from typing import Any

import pytest
from bs4 import BeautifulSoup, Tag
from django.core.exceptions import ValidationError
from django.test.client import Client
from django.urls.base import reverse
from ulid import ULID

from example.models import Item
from tests.data import ULID_HEX, ULID_STR, ULID_UUID, ULID_VALUE
from ulid_django.forms import ULIDField

INVALID_VALUES = [
    "Z" * 32,
    "0" * 30,
    "?" * 26,
]


class TestULIDField:
    @pytest.fixture
    def ulid_field(self) -> ULIDField:
        return ULIDField()

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (None, None),
            (ULID_STR, ULID_STR),
            (ULID_VALUE, ULID_STR),
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
        ("value", "expected"),
        [
            (None, None),
            ("", None),
            (ULID_VALUE, ULID_VALUE),
            (ULID_STR, ULID_VALUE),
            (ULID_HEX, ULID_VALUE),
            (str(ULID_UUID), ULID_VALUE),
        ],
    )
    def test_to_python(
        self,
        ulid_field: ULIDField,
        value: Any,
        expected: ULID | None,
    ) -> None:
        assert ulid_field.to_python(value) == expected

    @pytest.mark.parametrize("value", INVALID_VALUES)
    def test_to_python_invalid(self, ulid_field: ULIDField, value: Any) -> None:
        with pytest.raises(ValidationError) as exc_info:
            ulid_field.to_python(value)
        assert exc_info.value.code == "invalid"
        assert "ULID" in exc_info.value.message


@pytest.mark.django_db
class TestIntegration:
    @pytest.mark.parametrize("value", [ULID_STR, ULID_HEX])
    def test_form_get_set(self, admin_client: Client, item: Item, value: str) -> None:
        Item.objects.filter(pk=item.pk).update(etag=None)

        url = reverse("admin:example_item_change", args=[item.pk])

        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK
        soup = BeautifulSoup(response.content, "lxml")
        etag_field = soup.find("input", {"name": "etag"})
        assert isinstance(etag_field, Tag)
        assert etag_field.get("value") is None

        form_data = {
            "name": item.name,
            "etag": value,
            "_save": "Save",
        }
        response = admin_client.post(url, form_data, follow=True)
        assert response.status_code == HTTPStatus.OK

        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK
        soup = BeautifulSoup(response.content, "lxml")
        etag_field = soup.find("input", {"name": "etag"})
        assert isinstance(etag_field, Tag)
        assert etag_field.get("value") == ULID_STR

    @pytest.mark.parametrize("value", INVALID_VALUES)
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
        assert isinstance(etag_error_list, Tag)
        assert "ULID" in etag_error_list.text
