from typing import List

import pymongo

from fastapi import FastAPI, Body, Depends, HTTPException, WebSocket
from pydantic import UUID4

from app.model import UserSchema, UserLoginSchema
from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import signJWT
from fastapi.encoders import jsonable_encoder
from urllib.parse import unquote

# Chat Imports
import logging

from app.utils import parse_json

logger = logging.getLogger(__name__)


uri = 'mongodb+srv://artpel:artyty@treffendb.esk4d.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
client = pymongo.MongoClient(uri)
db = client.Users
db_Relationship = client.Relationship
db_POI = client.POI
db_Chat = client.Chat

app = FastAPI()


@app.get("/", tags=["root"])
async def read_root() -> dict:
    return {"message": "Welcome to Treffen API!."}


@app.get("/posts", dependencies=[Depends(JWTBearer())], tags=["posts"])
async def read_post() -> dict:
    return {"message": "My protected Post"}


@app.post("/user/signup", tags=["user"])
async def create_user(user: UserSchema = Body(...)):
    valid = await check_signup(user)
    if valid:
        user = jsonable_encoder(user)
        db["Users"].insert_one(user)
        return signJWT(user['email'])
    else:
        raise HTTPException(status_code=500, detail="Invalid User")


@app.post("/user/login", tags=["user"])
async def user_login(user: UserLoginSchema = Body(...)):
    valid = await check_user(user)
    if valid:
        return signJWT(user.email)
    raise HTTPException(status_code=500, detail="wrong Login")


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


# return user info from id
@app.get("/user/info/id/{user_id}", tags=["user"])
async def user_info_by_id(user_id: str):
    user_id = unquote(user_id)
    json_results = []
    for results in db.Users.find({"id": user_id}):
        json_results.append(results)
    if json_results:
        return parse_json(json_results[0])
    else:
        raise HTTPException(status_code=500, detail='No id Found')


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


# Adding friends without any need of request
@app.post("/relationship/{user_id}/add_friend/{target_user_id}")
async def create_relationship(user_id: str, target_user_id: str):
    user_id = unquote(user_id)
    target_user_id = unquote(target_user_id)
    valid = await check_relationship(user_id, target_user_id)
    if valid:
        results = {
            "FRIEND": "TRUE",
            "user_id": user_id,
            "friend_id": target_user_id
        }
        db_Relationship.Relationship.insert_one(results)
    else:
        raise HTTPException(status_code=500, detail="Invalid Relationship")


# Check for users already friends and similar ids
async def check_relationship(user_id: str, target_user_id: str):
    for results in db_Relationship.Relationship.find({"user_id": user_id, "friend_id": target_user_id}):
        if results:
            return False
    for results in db_Relationship.Relationship.find({"user_id": target_user_id, "friend_id": user_id}):
        if results:
            return False
    if user_id == target_user_id:
        return False
    return True


# Take an id and retreive friend list
@app.get("/user/{user_id}/friends", tags=["friends"])
async def get_friends(user_id: str):
    user_id = unquote(user_id)
    output = []
    for results in db_Relationship.Relationship.find({"user_id": user_id}):
        output.append(results)
    for results in db_Relationship.Relationship.find({"friend_id": user_id}):
        output.append(results)
    if output:
        return parse_json(output)
    else:
        raise HTTPException(status_code=500, detail='No Relation Found')


############ POI API ############


############ CHAT ###############

# Create a new chat (2 people)
@app.post("/chat/private/{user1_id}/{user2_id}", tags=["individual chat"])
async def create_chat(user1_id: str, user2_id: str):
    user1_id = unquote(user1_id)
    user2_id = unquote(user2_id)
    valid = await check_private_chat(user1_id, user2_id)
    if valid:
        chat_id = UUID4
        results = {
            "id": chat_id,
            "user1_id": user1_id,
            "user2_id": user2_id
        }
        db_Chat.Chat.insert_one(results)
    else:
        raise HTTPException(status_code=500, detail="Invalid Private Chat Demand")


# Check if the chat already exist
async def check_private_chat(user1_id: str, user2_id: str):
    for results in db_Chat.Chat.find({"user1_id": user1_id, "user2_id": user2_id}):
        if results:
            return False
    for results in db_Relationship.Relationship.find({"user1_id": user2_id, "user2_id": user1_id}):
        if results:
            return False
    if user1_id == user2_id:
        return False
    return True


# Get chat info from 2 user id
@app.get("/chat/{user1_id}/{user2_id}", tags=["individual chat"])
async def get_private_chat(user1_id: str, user2_id: str):
    user1_id = unquote(user1_id)
    user2_id = unquote(user2_id)
    output = []
    for results in db_Chat.Chat.find({"user1_id": user1_id, "user2_id": user2_id}):
        output.append(results)
    for results in db_Relationship.Relationship.find({"user1_id": user2_id, "user2_id": user1_id}):
        output.append(results)
    if not output:
        raise HTTPException(status_code=500, detail="This chat doesn't exit !")
    else:
        return output


# Chat Service #

class SocketManager:
    def __init__(self):
        self.active_connections: List[(WebSocket, str)] = []

    async def connect(self, websocket: WebSocket, user: str):
        await websocket.accept()
        self.active_connections.append((websocket, user))

    def disconnect(self, websocket: WebSocket, user: str):
        self.active_connections.remove((websocket, user))

    async def broadcast(self, data: dict):
        for connection in self.active_connections:
            await connection[0].send_json(data)


manager = SocketManager()
"""
async def upload_message_to_room():


# For private chat only
@app.websocket("/chat/private/{chat_id}/{user_id}")
async def chat(websocket: WebSocket, chat_id: str, user_id: str):
    chat_id = unquote(chat_id)
    user_id = unquote(user_id)
    try:
        # Add User
        await manager.connect(websocket, chat_id)
        data = {
            "content": f"{user_id} has entered the chat",
            "user": {"username": user_id},
            "room_name": chat_id,
            "type": "entrance",
        }
        await manager.broadcast(data)
        # Wait for message
        while True:
            if websocket.application_state == WebSocketState.CONNECTED:
                data = await websocket.receive_text()
                message_data = json.loads(data)
                if "type" in message_data and message_data["type"] == "dismissal":
                    logger.warning(message_data["content"])
                    logger.info("Disconnecting from Websocket")
                    await manager.disconnect(websocket, chat_id)
                    break
                else:
                    await upload_message_to_room(data)
                    logger.info(f"DATA RECIEVED: {data}")
                    await manager.broadcast(f"{data}")
            else:
                logger.warning(f"Websocket state: {websocket.application_state}, reconnecting...")
                await manager.connect(websocket, chat_id)
            except Exception as ex:
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            logger.error(message)
            # remove user
            logger.warning("Disconnecting Websocket")
            await remove_user_from_room(None, chat_id, username=user_id)
            room = await get_room(chat_id)
            data = {
                "content": f"{user_id} has left the chat",
                "user": {"username": chat_id},
                "room_name": chat_id,
                "type": "dismissal",
            }
            await manager.broadcast(f"{json.dumps(data, default=str)}")
            await manager.disconnect(websocket, chat_id)

    except
"""