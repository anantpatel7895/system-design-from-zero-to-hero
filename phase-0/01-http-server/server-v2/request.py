class Request:

    def __init__(
        self,
        method,
        path,
        version,
        headers,
        body
    ):
        self.method = method
        self.path = path
        self.version = version
        self.headers = headers
        self.body = body


def parse_request(raw_request):

    text = raw_request.decode()

    parts = text.split("\r\n\r\n", 1)

    header_part = parts[0]

    body = ""

    if len(parts) > 1:
        body = parts[1]

    lines = header_part.split("\r\n")

    request_line = lines[0]

    method, path, version = request_line.split()

    headers = {}

    for line in lines[1:]:

        if ":" in line:

            key, value = line.split(":", 1)

            headers[key.strip()] = value.strip()

    return Request(
        method=method,
        path=path,
        version=version,
        headers=headers,
        body=body
    )