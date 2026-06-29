from app import app

from network.server import Server

# Register routes
import examples.hello
import examples.users


if __name__ == "__main__":

    server = Server(
        app.router
    )

    server.start()