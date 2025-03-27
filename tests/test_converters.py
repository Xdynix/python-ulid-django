import pytest
from django.test.client import Client
from django.urls.base import reverse
from ulid import ULID

from ulid_django.converters import ULIDConverter

ulid = ULID()
ulid_str = str(ulid)

invalid_values = [
    "foobar",
    "8" + "0" * 25,
    ulid_str.lower(),
]


class TestULIDConverter:
    @pytest.fixture
    def ulid_converter(self) -> ULIDConverter:
        return ULIDConverter()

    def test_to_python(self, ulid_converter: ULIDConverter) -> None:
        assert ulid_converter.to_python(ulid_str) == ulid

    @pytest.mark.parametrize("value", invalid_values)
    def test_to_python_invalid(self, ulid_converter: ULIDConverter, value: str) -> None:
        with pytest.raises(ValueError):
            ulid_converter.to_python(value)

    def test_to_url(self, ulid_converter: ULIDConverter) -> None:
        assert ulid_converter.to_url(ulid) == ulid_str


class TestIntegration:
    def test_resolve(self, client: Client) -> None:
        response = client.get(f"/example/dummy/{ulid_str}/")
        assert response.status_code == 200
        assert response.content == b"OK"

    @pytest.mark.parametrize("value", invalid_values)
    def test_resolve_invalid(self, client: Client, value: str) -> None:
        response = client.get(f"/example/dummy/{value}/")
        assert response.status_code == 404

    @pytest.mark.parametrize("value", [ulid, ulid_str])
    def test_reverse(self, value: ULID | str) -> None:
        url = reverse("dummy_view", kwargs={"item_id": value})
        assert url == f"/example/dummy/{ulid_str}/"
