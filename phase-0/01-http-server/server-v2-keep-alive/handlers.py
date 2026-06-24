import json
import time
from response import Response


def hello(request):

    return Response(
        body="Hello User"
    )


def users(request):

    users_data = [
        "anant",
        "john",
        "alice"
    ]

    return Response(
        body=json.dumps(users_data),
        content_type="application/json"
    )


def health(request):

    return Response(
        body='{"status":"UP"}',
        content_type="application/json"
    )


def create_user(request):

    return Response(
        body=f"Received: {request.body}",
        status=201
    )



def slow(request):

    print("START SLOW REQUEST")

    time.sleep(20)

    print("END SLOW REQUEST")

    return Response("Done")