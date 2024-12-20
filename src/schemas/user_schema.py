from pydantic import BaseModel


class UserCreate(BaseModel):
    userid: int
    sname: str
    dname: str
    accesskey: str

    class Config:
        orm_mode = True
