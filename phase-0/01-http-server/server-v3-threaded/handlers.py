import json
import time

from response import Response


def hello(request):

    return Response(
        "Hello User"
    )


def users(request):

    return Response(
        json.dumps(
            [
                "anant",
                "john",
                "alice"
            ]
        ),
        content_type="application/json"
    )


def health(request):

    return Response(
        '{"status":"UP"}',
        content_type="application/json"
    )


def slow(request):

    print(
        "START SLOW REQUEST"
    )

    time.sleep(20)

    print(
        "END SLOW REQUEST"
    )

    return Response(
        "Done"
    )