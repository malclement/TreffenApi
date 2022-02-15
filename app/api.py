import json

from bson import json_util
from fastapi import FastAPI, Body, Depends, HTTPException
from app.model import UserSchema, UserLoginSchema
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import signJWT
from fastapi.encoders import jsonable_encoder
from urllib.parse import unquote

import pymongo

uri = 'mongodb+srv://artpel:artyty@treffendb.esk4d.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
client = pymongo.MongoClient(uri)
db = client.Users

app = FastAPI()


@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to Treffen API!."}


@app.post("/user/signup", tags=["user"])
async def create_user(user: UserSchema = Body(...)):
    valid = await check_signup(user)
    if valid:
        user = jsonable_encoder(user)
        new_user = db["Users"].insert_one(user)
        return signJWT(user['email'])
    else:
        raise HTTPException(status_code=500, detail="Invalid User")


@app.post("/user/login", tags=["user"])
async def user_login(user: UserLoginSchema = Body(...)):
    valid = await check_user(user)
    if valid:
        return signJWT(user.email)
    raise HTTPException(status_code=500, detail="wrong Login")


@app.get("/posts", dependencies=[Depends(JWTBearer())], tags=["posts"])
async def read_post() -> dict:
    return {"message": "My protected Post"}


# allows to serialize ObjectId
# used in @app.get("/user/info/{user_email}", tags=["user"])
def parse_json(data):
    return json.loads(json_util.dumps(data))


# return user info from is email
@app.get("/user/info/{user_email}", tags=["user"])
async def user_info(user_email: str):
    user_email = unquote(user_email)
    print(user_email)
    json_results = []
    for results in db.Users.find({"email": user_email}):
        json_results.append(results)
    return parse_json(json_results[0])


async def check_user(data: UserLoginSchema):
    for results in db.Users.find({"email": data.email}):
        if results['password'] == data.password:
            return True
        else:
            return False


async def check_signup(data: UserSchema):
    for results in db.Users.find({"email": data.email}):
        if results['email'] != "":
            return False
    return True
