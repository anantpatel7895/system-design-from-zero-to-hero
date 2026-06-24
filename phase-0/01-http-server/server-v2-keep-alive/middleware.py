from datetime import datetime


def log_request(request):

    print(
        f"[{datetime.now()}] "
        f"{request.method} "
        f"{request.path}"
    )


def log_headers(request):

    print("HEADERS:")

    for k, v in request.headers.items():

        print(f"{k}: {v}")