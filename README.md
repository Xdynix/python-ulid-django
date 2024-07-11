# python-ulid-django

[ULID (Universally Unique Lexicographically Sortable Identifier)][ulid-spec] support for
Django.

This package uses the ULID type implemented by [`python-ulid`][python-ulid].

> This package is heavily inspired by [`django-ulid`][django-ulid]. The reason I'm
> reinventing the wheel is that I want to use `python-ulib`[python-ulid]'s
> implementation.

## Usage

(TODO)

## Development

Prerequisite: [PDM](https://pdm-project.org/latest/)

Environment setup: `pdm sync`

Run linters: `pdm lint`

[ulid-spec]: https://github.com/ulid/spec

[python-ulid]: https://github.com/mdomke/python-ulid

[django-ulid]: https://github.com/ahawker/django-ulid
