from typing import Any
from uuid import UUID

import pytest
from django.core.exceptions import ValidationError
from django.db.models import UUIDField
from pytest_mock import MockerFixture
from ulid import ULID
from ulid_django.forms import ULIDField as ULIDFormField
from ulid_django.models import ULIDField

ulid = ULID()
ulid_int = int(ulid)
ulid_str = str(ulid)
ulid_hex = ulid.hex
ulid_uuid = ulid.to_uuid()


class TestULIDField:
    @pytest.fixture
    def ulid_field(self) -> ULIDField:
        return ULIDField()

    @pytest.mark.parametrize(
        "value, expected",
        [
            (None, None),
            (ulid, ulid),
            (ulid_int, ulid),
            (ulid_str, ulid),
            (ulid_hex, ulid),
            (ulid_uuid, ulid),
            (ulid_uuid.hex, ulid),
            (str(ulid_uuid), ulid),
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
            "foobar",
            "Z" * 32,
            "0" * 30,
            "?" * 26,
            [],
            (),
        ],
    )
    def test_to_python_invalid(self, ulid_field: ULIDField, value: Any) -> None:
        with pytest.raises(ValidationError) as exc_info:
            ulid_field.to_python(value)
        assert exc_info.value.code == "invalid"
        assert "ULID" in exc_info.value.message

    @pytest.mark.parametrize(
        "value, expected",
        [
            (None, None),
            (ulid_hex, ulid),
            (ulid_uuid, ulid),
        ],
    )
    def test_from_db_value(
        self,
        ulid_field: ULIDField,
        value: Any,
        expected: ULID,
    ) -> None:
        assert ulid_field.from_db_value(value) == expected

    @pytest.mark.parametrize(
        "value, expected",
        [
            (None, None),
            (ulid, ulid_uuid),
        ],
    )
    def test_get_prep_value(
        self,
        ulid_field: ULIDField,
        value: Any,
        expected: UUID | None,
    ) -> None:
        assert ulid_field.get_prep_value(value) == expected

    @pytest.mark.parametrize("has_native_uuid_field", [True, False])
    @pytest.mark.parametrize(
        "ulid_val, uuid_val",
        [
            (None, None),
            (ulid, ulid_uuid),
        ],
    )
    def test_get_db_prep_value(
        self,
        mocker: MockerFixture,
        ulid_field: ULIDField,
        has_native_uuid_field: bool,
        ulid_val: ULID | None,
        uuid_val: UUID | None,
    ) -> None:
        connection = mocker.MagicMock()
        connection.features.has_native_uuid_field = has_native_uuid_field
        ulid_db_prep_value = ulid_field.get_db_prep_value(ulid_val, connection)
        uuid_db_prep_value = UUIDField().get_db_prep_value(uuid_val, connection)
        assert ulid_db_prep_value == uuid_db_prep_value

    def test_formfield(self, ulid_field: ULIDField) -> None:
        assert isinstance(ulid_field.formfield(), ULIDFormField)
