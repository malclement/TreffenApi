from typing import Optional, List

import datetime as dt
from pydantic import BaseModel
from uuid import UUID


class ChatMessage(BaseModel):
    id: Optional[UUID]
    send_at: Optional[dt.datetime]
    from_profile_id: UUID
    chat_group_id: UUID
    content: str


class ChatGroup(BaseModel):
    id: Optional[UUID]
    name: Optional[str]
    private: bool = True
    members: Optional[List[UUID]] = []


class PrivateChat(BaseModel):
    id: Optional[UUID]
    user1_id: UUID
    user2_id: UUID
