"""
Synchronous handler example.
"""

from app import App

app = App()


@app.get("/")
def home(request):

    return {
        "message": "Hello Sync"
    }


if __name__ == "__main__":

    app.run()