from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserLogin(BaseModel):
    access_token: str


class UserBase(BaseModel):
    gid: str
    gname: str
    picture: str
    access_key: str
    last_access_time: datetime

    model_config = ConfigDict(from_attributes=True)
