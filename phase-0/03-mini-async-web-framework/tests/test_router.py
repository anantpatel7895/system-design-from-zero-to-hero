from http.router import Router


def test_router():

    router = Router()

    @router.get("/hello")
    def hello(request):

        return "Hello"

    handler = router.resolve(
        "GET",
        "/hello",
    )

    assert handler is hello