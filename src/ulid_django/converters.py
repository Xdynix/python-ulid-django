from typing import cast

from ulid import ULID


class ULIDConverter:
    regex = "[A-Z0-9]{26}"

    def to_python(self, value: str) -> ULID:
        return cast(ULID, ULID.from_str(value))

    def to_url(self, value: ULID) -> str:
        return str(value)
