from http.router import Router
from http.request_processor import RequestProcessor
from core.context import Context


class DummyConnection:

    keep_alive = True


def test_processor():

    router = Router()

    @router.get("/hello")
    def hello(request):

        return {
            "msg": "hello"
        }

    processor = RequestProcessor(
        router
    )

    raw = (
        b"GET /hello HTTP/1.1\r\n"
        b"\r\n"
    )

    context = Context(
        DummyConnection()
    )

    processor.process(
        context,
        raw,
    )

    assert context.response.status == 200