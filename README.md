# python-ulid-django

[ULID (Universally Unique Lexicographically Sortable Identifier)][ulid-spec] support for
Django.

This package uses the ULID type implemented by [`python-ulid`][python-ulid].

> This package is heavily inspired by [`django-ulid`][django-ulid]. The reason I'm
> reinventing the wheel is that I want to use [`python-ulib`][python-ulid]'s
> ULID implementation.

## Usage

### Installation

```shell
pip install python-ulid-django
```

### Model Field

You can then add `ULIDField` to your Django model just like other fields.

Example:

```python
from django.contrib.auth.models import AbstractUser
from ulid import ULID
from ulid_django.models import ULIDField


class User(AbstractUser):
    id = ULIDField(primary_key=True, default=ULID, editable=False)
```

### URL Converter

There is also a URL converter can be used.

```python
from django.urls import path, register_converter
from ulid import ULID
from ulid_django.converters import ULIDConverter


def user_detail_view(request, user_id):
    assert isinstance(user_id, ULID)
    ...


register_converter(ULIDConverter, "ulid")

urlpatterns = [
    path("user/<ulid:user_id>/", user_detail_view),
    ...,
]
```

## Development

Prerequisite: [PDM](https://pdm-project.org/latest/)

Environment setup: `pdm sync`

Run linters: `pdm lint`

Test: `pdm test`

[ulid-spec]: https://github.com/ulid/spec

[python-ulid]: https://github.com/mdomke/python-ulid

[django-ulid]: https://github.com/ahawker/django-ulid
