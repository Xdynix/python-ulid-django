from ulid import ULID


class ULIDConverter:
    # Crockford base32 omits I, L, O and U. 26 characters carry 130 bits, so the
    # leading one has only 3 significant bits and cannot exceed 7.
    regex = "[0-7][0-9ABCDEFGHJKMNPQRSTVWXYZ]{25}"

    def to_python(self, value: str) -> ULID:
        return ULID.from_str(value)

    def to_url(self, value: ULID | str) -> str:
        return str(value)
