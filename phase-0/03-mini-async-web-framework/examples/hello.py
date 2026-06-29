from app import app




@app.get("/hello")
def hello(request):

    return {
        "message": "Hello World"
    }