from app import app


@app.get("/users")
def users(request):

    return [
        "Alice",
        "Bob",
        "Charlie",
    ]