from ulid import ULID


class ULIDConverter:
    regex = "[A-Z0-9]{26}"

    @classmethod
    def to_python(cls, value: str) -> ULID:
        return ULID.from_str(value)

    @classmethod
    def to_url(cls, value: ULID) -> str:
        return str(value)
