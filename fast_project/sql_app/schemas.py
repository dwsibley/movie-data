from datetime import date, datetime
from typing import List, Union, Optional
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

class NetflixNameBase(BaseModel):
    name: str

    class Config:
        orm_mode = True

class NetflixNameResponse(NetflixNameBase):
    id: int

class NetflixCountryBase(BaseModel):
    name: str

    class Config:
        orm_mode = True

class NetflixCountryResponse(NetflixCountryBase):
    id: int

class NetflixCategoryBase(BaseModel):
    name: str

    class Config:
        orm_mode = True

class NetflixCategoryResponse(NetflixCategoryBase):
    id: int

class NetflixTitleBase(BaseModel):
    #show_id: str
    title: str
    #country: str
    release_year: int
    duration: Union[int, None]
    seasons: Union[int, None]
    description: str

    class Config:
        orm_mode = True
    
class NetflixTitleCreate(NetflixTitleBase):
    show_id: str
    date_added: Union[str, None]
    directors: list #TODO: could update this field and other to use Name Schema
    cast: list
    countries: list
    categories: list
    rating: Union[str, None]
    title_type: str

class NetflixTitlePut(NetflixTitleBase):
    date_added: Union[str, None]
    directors: list #TODO: could update this field and other to use Name Schema
    cast: list
    countries: list
    categories: list
    rating: Union[str, None]
    title_type: str

class NetflixTitlePatch(BaseModel):
    #show_id: str
    title: Optional[str]
    #country: str
    release_year: Optional[int]
    duration: Optional[int] = ...
    seasons: Optional[int] = ...
    description: Optional[str]
    date_added: Optional[str] = ...
    directors: Optional[list]
    cast: Optional[list]
    countries: Optional[list]
    categories: Optional[list]
    rating: Optional[str] = ...
    title_type: Optional[str]

    class Config:
        orm_mode = True

class NetflixTitleResponse(NetflixTitleBase):
    id: int
    show_id: str
    #title_type_id: int
    title_type: str
    directors: List[NetflixNameResponse]
    #directors: List[str]
    cast: List[NetflixNameResponse]
    countries: List[NetflixCountryResponse]
    categories: List[NetflixCategoryResponse]
    date_added: date
    created_at: datetime
    updated_at: datetime
    #rating_id: int
    rating: str
