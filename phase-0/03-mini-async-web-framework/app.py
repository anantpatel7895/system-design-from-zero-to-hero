"""
Application object.
"""

from network.server import Server
from http.router import Router


class App:

    def __init__(self):

        self.router = Router()

    def get(
        self,
        path,
    ):

        return self.router.get(path)

    def post(
        self,
        path,
    ):

        return self.router.post(path)

    def run(self):

        server = Server(
            self.router
        )

        server.start()

app = App()