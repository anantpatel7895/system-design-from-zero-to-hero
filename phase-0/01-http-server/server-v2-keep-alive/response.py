STATUS_CODES = {
    200: "200 OK",
    201: "201 Created",
    400: "400 Bad Request",
    404: "404 Not Found",
    500: "500 Internal Server Error"
}


class Response:

    def __init__(
        self,
        body,
        status=200,
        content_type="text/plain"
    ):
        self.body = body
        self.status = status
        self.content_type = content_type


def build_response(response):

    body = response.body

    return (
        f"HTTP/1.1 {STATUS_CODES[response.status]}\r\n"
        f"Content-Type: {response.content_type}\r\n"
        f"Content-Length: {len(body.encode())}\r\n"
        f"Connection: keep-alive\r\n"
        f"\r\n"
        f"{body}"
    )