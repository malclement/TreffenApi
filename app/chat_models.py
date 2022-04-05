from typing import Optional, List

import datetime as dt
from pydantic import BaseModel
from uuid import UUID


class Message(BaseModel):
    message_id: Optional[UUID]
    send_at: Optional[dt.datetime]
    from_profile_id: UUID
    chat_group_id: UUID
    content: str


class GroupChat(BaseModel):
    group_chat_id: Optional[UUID]
    name: Optional[str]
    private: bool = True
    members: Optional[List[UUID]] = []


class PrivateChat(BaseModel):
    private_chat_id: Optional[UUID]
    user1_id: UUID
    user2_id: UUID
