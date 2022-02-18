import json
import pymongo

from bson import json_util
from fastapi import FastAPI, Body, Depends, HTTPException
from app.model import UserSchema, UserLoginSchema
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import signJWT
from fastapi.encoders import jsonable_encoder
from urllib.parse import unquote

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
    json_results = []
    for results in db.Users.find({"email": user_email}):
        json_results.append(results)
    if json_results:
        return parse_json(json_results[0])
    else:
        raise HTTPException(status_code=500, detail='No User Found')


# Return the info of every user with {friend_name}
# Output is a list of json
@app.get("/user/other/search/{friend_name}", tags=["friends"])
async def search_friend(friend_name: str):
    output = []
    friend_name = unquote(friend_name)
    for results in db.Users.find({"fullname": friend_name}):
        assert isinstance(results, object)
        output.append(results)
    if output:
        return parse_json(output)
    else:
        raise HTTPException(status_code=500, detail='No User Found')


def compare_names(name1: str, name2: str):
    typed_name = name1.split()
    searched_name = name2.split()
    for i in range(len(typed_name)):
        for j in range(len(searched_name)):
            if typed_name[i] != searched_name[j]:
                break
    return 0


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
