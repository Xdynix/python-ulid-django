from django.http import HttpRequest, HttpResponse
from ulid import ULID


def dummy_view(_: HttpRequest, item_id: ULID) -> HttpResponse:
    if not isinstance(item_id, ULID):
        return HttpResponse(status=400)
    return HttpResponse("OK")
