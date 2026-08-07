# python-ulid-django

[ULID (Universally Unique Lexicographically Sortable Identifier)][ulid-spec] support for
Django.

This package uses the ULID type implemented by [`python-ulid`][python-ulid].

> This package is heavily inspired by [`django-ulid`][django-ulid]. The reason I'm
> reinventing the wheel is that I want to use [`python-ulid`][python-ulid]'s
> ULID implementation.

## Requirements

Python 3.12+ and Django 5.2+.

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

### Form Field

`ULIDField` supplies a matching form field automatically, so a `ModelForm` needs
no extra wiring. Use it directly when building a plain form:

```python
from django import forms
from ulid_django.forms import ULIDField


class LookupForm(forms.Form):
    item_id = ULIDField()
```

It cleans to a `ULID` and accepts three input widths: the 26-character canonical
representation, a 32-character hex string, and a 36-character UUID string.

### URL Converter

A URL converter is also provided.

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

Prerequisite: [uv](https://docs.astral.sh/uv/) and [just](https://just.systems/)

Environment setup: `just dev-setup`

Run linters: `just lint`

Test: `just test`

Test against every supported Python version: `just test-all`

[ulid-spec]: https://github.com/ulid/spec

[python-ulid]: https://github.com/mdomke/python-ulid

[django-ulid]: https://github.com/ahawker/django-ulid
