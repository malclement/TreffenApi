from fastapi import FastAPI
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/id")
async def root():
    return {"message": "Hello You"}
