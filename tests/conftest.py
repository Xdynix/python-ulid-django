import pytest

from example.models import Item
from tests.data import ULID_VALUE


@pytest.fixture
def item() -> Item:
    return Item.objects.create(name="item", etag=ULID_VALUE)
