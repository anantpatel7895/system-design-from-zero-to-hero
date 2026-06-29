"""
Keep Alive Demo

Run:

curl -v \
     --http1.1 \
     --header "Connection: keep-alive" \
     http://localhost:8080/

Repeat multiple requests
without restarting the server.
"""

from app import App

app = App()


counter = 0


@app.get("/")
def home(request):

    global counter

    counter += 1

    return {
        "requests": counter
    }


if __name__ == "__main__":

    app.run()