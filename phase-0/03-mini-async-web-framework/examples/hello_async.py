"""
Asynchronous handler example.
"""

from app import App
from runtime.future import Future

app = App()


async def fake_db():

    future = Future()

    future.set_result(
        {
            "name": "Anant"
        }
    )

    return await future


@app.get("/")
async def home(request):

    user = await fake_db()

    return user


if __name__ == "__main__":

    app.run()