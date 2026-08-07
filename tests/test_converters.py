from http import HTTPStatus

import pytest
from django.test.client import Client
from django.urls.base import reverse
from ulid import ULID

from tests.data import ULID_STR, ULID_VALUE
from ulid_django.converters import ULIDConverter

INVALID_VALUES: tuple[tuple[str, str], ...] = (
    ("foobar", "exactly 26 characters long"),
    ("8" + "0" * 25, "too large and will overflow"),
    ("0" + "I" * 25, "can only consist of letters"),
    (ULID_STR.lower(), "can only consist of letters"),
)


class TestULIDConverter:
    @pytest.fixture
    def ulid_converter(self) -> ULIDConverter:
        return ULIDConverter()

    def test_to_python(self, ulid_converter: ULIDConverter) -> None:
        assert ulid_converter.to_python(ULID_STR) == ULID_VALUE

    @pytest.mark.parametrize(("value", "message"), INVALID_VALUES)
    def test_to_python_invalid(
        self,
        ulid_converter: ULIDConverter,
        value: str,
        message: str,
    ) -> None:
        with pytest.raises(ValueError, match=message):
            ulid_converter.to_python(value)

    def test_to_url(self, ulid_converter: ULIDConverter) -> None:
        assert ulid_converter.to_url(ULID_VALUE) == ULID_STR


class TestIntegration:
    def test_resolve(self, client: Client) -> None:
        response = client.get(f"/example/dummy/{ULID_STR}/")
        assert response.status_code == HTTPStatus.OK
        assert response.content == b"OK"

    @pytest.mark.parametrize("value", [value for value, _ in INVALID_VALUES])
    def test_resolve_invalid(self, client: Client, value: str) -> None:
        response = client.get(f"/example/dummy/{value}/")
        assert response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize("value", [ULID_VALUE, ULID_STR])
    def test_reverse(self, value: ULID | str) -> None:
        url = reverse("dummy_view", kwargs={"item_id": value})
        assert url == f"/example/dummy/{ULID_STR}/"
