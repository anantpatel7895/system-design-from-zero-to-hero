STATUS_CODES = {
    200: "200 OK",
    404: "404 Not Found",
    500: "500 Internal Server Error"
}


def build_response(status_code, body):

    status = STATUS_CODES.get(
        status_code,
        "500 Internal Server Error"
    )

    response = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: text/plain\r\n"
        f"Content-Length: {len(body.encode())}\r\n"
        f"Connection: keep-alive\r\n"
        f"\r\n"
        f"{body}"
    )

    return response