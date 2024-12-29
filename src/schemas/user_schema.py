from pydantic import BaseModel


class UserCreate(BaseModel):
    xid: int
    sname: str
    dname: str
    accesskey: str

    class Config:
        orm_mode = True
