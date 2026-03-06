from fastapi import FastAPI
import pocketbase

pb = pocketbase.PocketBase("http://pocketbase:8080")
app = FastAPI()


@app.get("/")
def root():
    return "Hello World"


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
