from fastapi import FastAPI
import pymongo
import os
uri = 'mongodb+srv://artpel:artyty@treffendb.esk4d.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
client = pymongo.MongoClient(uri)
db = client.treffendb


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

