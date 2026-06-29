from datetime import datetime


def log_request(request):

    print(
        f"[{datetime.now()}] "
        f"{request.method} "
        f"{request.path}"
    )