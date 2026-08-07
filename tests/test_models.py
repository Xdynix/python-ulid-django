from typing import Any
from uuid import UUID

import pytest
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.models import UUIDField
from pytest_mock import MockerFixture
from ulid import ULID

from example.models import Item
from tests.data import ULID_HEX, ULID_INT, ULID_STR, ULID_UUID, ULID_VALUE
from ulid_django.forms import ULIDField as ULIDFormField
from ulid_django.models import ULIDField

type ULIDModelField = ULIDField[ULID | UUID | str | int, ULID]

INVALID_VALUES = [
    "foobar",
    "Z" * 32,
    "0" * 30,
    "?" * 26,
    [],
    (),
]


class TestULIDField:
    @pytest.fixture
    def ulid_field(self) -> ULIDModelField:
        return ULIDField()

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (None, None),
            (ULID_VALUE, ULID_VALUE),
            (ULID_INT, ULID_VALUE),
            (ULID_STR, ULID_VALUE),
            (ULID_HEX, ULID_VALUE),
            (ULID_UUID, ULID_VALUE),
            (ULID_UUID.hex, ULID_VALUE),
            (str(ULID_UUID), ULID_VALUE),
        ],
    )
    def test_to_python(
        self,
        ulid_field: ULIDModelField,
        value: Any,
        expected: ULID | None,
    ) -> None:
        assert ulid_field.to_python(value) == expected

    @pytest.mark.parametrize("value", INVALID_VALUES)
    def test_to_python_invalid(self, ulid_field: ULIDModelField, value: Any) -> None:
        with pytest.raises(ValidationError) as exc_info:
            ulid_field.to_python(value)
        assert exc_info.value.code == "invalid"
        assert "ULID" in exc_info.value.message

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (None, None),
            (ULID_HEX, ULID_VALUE),
            (ULID_UUID, ULID_VALUE),
        ],
    )
    def test_from_db_value(
        self,
        ulid_field: ULIDModelField,
        value: Any,
        expected: ULID,
    ) -> None:
        assert ulid_field.from_db_value(value, None, connection) == expected

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (None, None),
            (ULID_VALUE, ULID_UUID),
        ],
    )
    def test_get_prep_value(
        self,
        ulid_field: ULIDModelField,
        value: Any,
        expected: UUID | None,
    ) -> None:
        assert ulid_field.get_prep_value(value) == expected

    @pytest.mark.parametrize("has_native_uuid_field", [True, False])
    @pytest.mark.parametrize(
        ("ulid_val", "uuid_val"),
        [
            (None, None),
            (ULID_VALUE, ULID_UUID),
        ],
    )
    def test_get_db_prep_value(
        self,
        mocker: MockerFixture,
        ulid_field: ULIDModelField,
        has_native_uuid_field: bool,
        ulid_val: ULID | None,
        uuid_val: UUID | None,
    ) -> None:
        connection = mocker.MagicMock()
        connection.features.has_native_uuid_field = has_native_uuid_field
        ulid_db_prep_value = ulid_field.get_db_prep_value(ulid_val, connection)
        uuid_db_prep_value = UUIDField().get_db_prep_value(uuid_val, connection)
        assert ulid_db_prep_value == uuid_db_prep_value

    def test_formfield(self, ulid_field: ULIDModelField) -> None:
        assert isinstance(ulid_field.formfield(), ULIDFormField)


@pytest.mark.django_db
class TestIntegration:
    @pytest.mark.parametrize(
        "value", [ULID_VALUE, ULID_INT, ULID_STR, ULID_HEX, ULID_UUID]
    )
    def test_query(self, item: Item, value: ULID | UUID | str | int) -> None:
        assert Item.objects.filter(etag=value).first() == item

    @pytest.mark.parametrize("value", INVALID_VALUES)
    def test_query_invalid(self, value: Any) -> None:
        with pytest.raises(ValidationError):
            Item.objects.filter(etag=value).get()

    @pytest.mark.parametrize(
        "value", [ULID_VALUE, ULID_INT, ULID_STR, ULID_HEX, ULID_UUID]
    )
    def test_get_set(self, item: Item, value: ULID | UUID | str | int) -> None:
        Item.objects.filter(pk=item.pk).update(etag=None)

        item.refresh_from_db()
        assert item.etag is None

        item.etag = value
        item.save()

        item.refresh_from_db()
        assert item.etag == ULID_VALUE
        assert isinstance(item.etag, ULID)

    @pytest.mark.parametrize("value", INVALID_VALUES)
    def test_set_invalid(self, item: Item, value: Any) -> None:
        item.etag = value
        with pytest.raises(ValidationError):
            item.save()
