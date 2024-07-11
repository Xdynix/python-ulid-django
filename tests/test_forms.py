from typing import Any

import pytest
from django.core.exceptions import ValidationError
from ulid import ULID
from ulid_django.forms import ULIDField

ulid = ULID()
ulid_str = str(ulid)
ulid_hex = ulid.hex


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

    @pytest.mark.parametrize(
        "value",
        [
            "Z" * 32,
            "0" * 30,
            "?" * 26,
        ],
    )
    def test_to_python_invalid(self, ulid_field: ULIDField, value: Any) -> None:
        with pytest.raises(ValidationError) as exc_info:
            ulid_field.to_python(value)
        assert exc_info.value.code == "invalid"
        assert "ULID" in exc_info.value.message
