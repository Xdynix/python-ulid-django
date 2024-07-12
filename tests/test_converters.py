import pytest
from ulid import ULID
from ulid_django.converters import ULIDConverter

ulid = ULID()
ulid_str = str(ulid)


class TestULIDConverter:
    @pytest.fixture
    def ulid_converter(self) -> ULIDConverter:
        return ULIDConverter()

    def test_to_python(self, ulid_converter: ULIDConverter) -> None:
        assert ulid_converter.to_python(ulid_str) == ulid

    @pytest.mark.parametrize(
        "value",
        [
            "8" + "0" * 25,
            ulid_str.lower(),
        ],
    )
    def test_to_python_invalid(self, ulid_converter: ULIDConverter, value: str) -> None:
        with pytest.raises(ValueError):
            ulid_converter.to_python(value)

    def test_to_url(self, ulid_converter: ULIDConverter) -> None:
        assert ulid_converter.to_url(ulid) == ulid_str
