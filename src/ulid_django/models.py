from typing import TYPE_CHECKING, Any, TypeVar, cast, override
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import models
from django.db.backends.base.base import BaseDatabaseWrapper
from django.forms import ChoiceField, Field
from django.utils.translation import gettext_lazy as _
from ulid import ULID

from ulid_django.forms import ULIDField as ULIDFormField

_ST = TypeVar("_ST", contravariant=True)
_GT = TypeVar("_GT", covariant=True)

if TYPE_CHECKING:
    _ULIDFieldBase = models.UUIDField[_ST, _GT]
else:
    # Django fields are not subscriptable without django_stubs_ext.monkeypatch().
    class _ULIDFieldBase(models.UUIDField):
        def __class_getitem__(cls, _item: Any) -> type:
            return cls


# Subscripting the base is what binds the parameters to Field.__get__: via
# Generic the descriptor still yields Any. Giving them defaults would pin
# null=True fields to a non-optional ULID; the plugin derives both per call site.
class ULIDField(_ULIDFieldBase[_ST, _GT]):
    """Django model field for ULID type.

    Check below for more details:

    - https://github.com/ulid/spec
    - https://github.com/mdomke/python-ulid
    """

    _pyi_private_set_type: ULID | UUID | str | int  # type: ignore[assignment]
    _pyi_private_get_type: ULID  # type: ignore[assignment]
    _pyi_lookup_exact_type: ULID | UUID | str | int  # type: ignore[assignment]

    description = _("Universally unique lexicographically sortable identifier")

    @override
    def to_python(self, value: Any) -> ULID | None:
        if value is None or isinstance(value, ULID):
            return value
        try:
            if isinstance(value, str) and len(value) == 26:
                return ULID.from_str(value)
            else:
                value = super().to_python(value)
                return ULID.from_uuid(value)
        except (ValueError, ValidationError) as err:
            raise ValidationError(
                _("%(value)r is not a valid ULID."),
                code="invalid",
                params={"value": value},
            ) from err

    def from_db_value(
        self,
        value: Any,
        _expression: Any,
        _connection: BaseDatabaseWrapper,
    ) -> ULID | None:
        return self.to_python(value)

    @override
    def get_prep_value(self, value: Any) -> UUID | None:
        value = super().get_prep_value(value)
        value = self.to_python(value)
        if value is None:
            return value
        return cast(UUID, value.to_uuid())

    @override
    def get_db_prep_value(
        self,
        value: Any,
        connection: BaseDatabaseWrapper,
        prepared: bool = False,
    ) -> Any:
        value = self.get_prep_value(value)
        return super().get_db_prep_value(value, connection, prepared)

    @override
    def formfield(
        self,
        form_class: type[Field] | None = None,
        choices_form_class: type[ChoiceField] | None = None,
        **kwargs: Any,
    ) -> Field | None:
        return super().formfield(
            form_class=form_class or ULIDFormField,
            choices_form_class=choices_form_class,
            **kwargs,
        )
