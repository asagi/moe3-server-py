from pydantic import BaseModel, ConfigDict


class UserLogin(BaseModel):
    access_token: str


class UserBase(BaseModel):
    xid: int
    screen_name: str
    display_name: str
    access_key: str

    model_config = ConfigDict(from_attributes=True)
