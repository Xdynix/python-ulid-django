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
    pytest.param([], id="empty_list"),
    pytest.param((), id="empty_tuple"),
]

VALID_VALUES = [
    pytest.param(ULID_VALUE, id="ulid"),
    pytest.param(ULID_INT, id="int"),
    pytest.param(ULID_STR, id="str"),
    pytest.param(ULID_HEX, id="hex"),
    pytest.param(ULID_UUID, id="uuid"),
]


class TestULIDField:
    @pytest.fixture
    def ulid_field(self) -> ULIDModelField:
        return ULIDField()

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (None, None),
            pytest.param(ULID_VALUE, ULID_VALUE, id="ulid"),
            pytest.param(ULID_INT, ULID_VALUE, id="int"),
            pytest.param(ULID_STR, ULID_VALUE, id="str"),
            pytest.param(ULID_HEX, ULID_VALUE, id="hex"),
            pytest.param(ULID_UUID, ULID_VALUE, id="uuid"),
            pytest.param(ULID_UUID.hex, ULID_VALUE, id="uuid_hex"),
            pytest.param(str(ULID_UUID), ULID_VALUE, id="uuid_str"),
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
            pytest.param(ULID_HEX, ULID_VALUE, id="hex"),
            pytest.param(ULID_UUID, ULID_VALUE, id="uuid"),
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
            pytest.param(ULID_VALUE, ULID_UUID, id="ulid"),
        ],
    )
    def test_get_prep_value(
        self,
        ulid_field: ULIDModelField,
        value: Any,
        expected: UUID | None,
    ) -> None:
        assert ulid_field.get_prep_value(value) == expected

    @pytest.mark.parametrize(
        "has_native_uuid_field",
        [
            pytest.param(True, id="native_uuid"),
            pytest.param(False, id="no_native_uuid"),
        ],
    )
    @pytest.mark.parametrize(
        ("ulid_val", "uuid_val"),
        [
            (None, None),
            pytest.param(ULID_VALUE, ULID_UUID, id="ulid"),
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
    @pytest.mark.parametrize("value", VALID_VALUES)
    def test_query(self, item: Item, value: ULID | UUID | str | int) -> None:
        assert Item.objects.filter(etag=value).first() == item

    @pytest.mark.parametrize("value", INVALID_VALUES)
    def test_query_invalid(self, value: Any) -> None:
        with pytest.raises(ValidationError):
            Item.objects.filter(etag=value).get()

    @pytest.mark.parametrize("value", VALID_VALUES)
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
