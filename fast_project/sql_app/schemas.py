from typing import Union
from pydantic import BaseModel

# class ItemBase(BaseModel):
#     title: str
#     description: str | None = None


# class ItemCreate(ItemBase):
#     pass


# class Item(ItemBase):
#     id: int
#     owner_id: int

#     class Config:
#         orm_mode = True


class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    #items: list[Item] = []

    class Config:
        orm_mode = True

class NetflixTitleBase(BaseModel):
    show_id: str
    title: str
    country: str
    release_year: int
    duration: Union[int, None]
    seasons: Union[int, None]
    description: str

    class Config:
        orm_mode = True
    
class NetflixTitleCreate(NetflixTitleBase):
    date_added: str
    directors: list
    cast: list
    categories: list
    rating: str
    title_type: str

class NetflixTitleResponse(NetflixTitleBase):
    id: int
