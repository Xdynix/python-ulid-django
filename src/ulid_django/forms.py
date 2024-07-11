from typing import Any, cast

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from ulid import ULID


class ULIDField(forms.CharField):
    default_error_messages = {  # noqa: RUF012
        "invalid": _("Enter a valid ULID."),
    }

    def prepare_value(self, value: Any) -> Any:
        if isinstance(value, ULID):
            return str(value)
        return value

    def to_python(self, value: Any) -> ULID | None:  # type: ignore[override]
        value = super().to_python(value)
        if value in self.empty_values:
            return None
        try:
            if len(value) == 26:
                value = ULID.from_str(value)
            elif len(value) == 32:
                value = ULID.from_hex(value)
            else:
                raise ValueError
        except ValueError as err:
            raise ValidationError(
                self.error_messages["invalid"],
                code="invalid",
            ) from err
        return cast(ULID, value)
