from network.connection import Connection


class FakeSocket:

    def __init__(self):

        self.sent = b""

    def recv(self, size):

        return (
            b"GET /hello HTTP/1.1\r\n"
            b"\r\n"
        )

    def sendall(self, data):

        self.sent = data

    def close(self):

        pass

    def setblocking(self, flag):

        pass