from email import header
import os

from fastapi import Depends, FastAPI, HTTPException, Header
from fastapi.security import APIKeyHeader
from pydantic import DurationError
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

# import crud, models, schemas
# from database import SessionLocal, engine

from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#FastAPI Filter stuff
class NetflixTitleTypeFilter(Filter):
    name: str
    order_by: list[str] | None

    class Constants(Filter.Constants):
        model = models.NetflixTitleType 

class NetflixTitleFilter(Filter):
    #title: str | None
    title_type: str | None
    #title_type: NetflixTitleTypeFilter = FilterDepends(with_prefix("_title_type", NetflixTitleTypeFilter))
    title_type__in: list[str] | None
    #date_added: #fastapi-filter may not support dates yet
    release_year: int | None
    #release_year__lt
    rating: str | None
    rating__in: list[str] | None
    duration: int | None
    seasons: int | None
    order_by: list[str] | None
    
    class Constants(Filter.Constants):
        model = models.NetflixTitle    

async def verify_api_key(authorization: str = Header()):
    valid = False
    header_prefix = 'Token '
    if authorization.find(header_prefix) == 0:
        token = authorization[len(header_prefix):]
        if token == os.environ.get('GENERAL_API_KEY'):
            valid = True
            print('Token valid!!!')
    if not(valid):
        raise HTTPException(status_code=401, detail="invalid token")

# End points 
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/netflix/titles/",  response_model=list[schemas.NetflixTitleResponse], dependencies=[Depends(verify_api_key)])
#def read_netflix_titles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#def read_netflix_titles(authorization: str | None = Header(default=None), netflix_title_filter: NetflixTitleFilter = FilterDepends(NetflixTitleFilter), skip: int = 0, limit: int = 100, search: str = None, db: Session = Depends(get_db)):
def read_netflix_titles(netflix_title_filter: NetflixTitleFilter = FilterDepends(NetflixTitleFilter), skip: int = 0, limit: int = 100, search: str = None, db: Session = Depends(get_db)):
    netflix_titles = crud.get_netflix_titles(db, skip=skip, limit=limit, search=search, netflix_title_filter=netflix_title_filter)
    return netflix_titles

@app.get("/netflix/titles/{show_id}", response_model=schemas.NetflixTitleResponse)
def read_netflix_title(show_id: str, db: Session = Depends(get_db)):
    netflix_title = crud.get_netflix_title_by_show_id(db, show_id=show_id)
    if netflix_title is None:
        raise HTTPException(status_code=404, detail="Netflix title not found")
    return netflix_title

@app.post("/netflix/titles/", response_model=schemas.NetflixTitleResponse)
def create_netflix_title(netflix_title: schemas.NetflixTitleCreate, db: Session = Depends(get_db)):
    db_netflix_title = crud.get_netflix_title_by_show_id(db, show_id=netflix_title.show_id)
    if db_netflix_title:
        raise HTTPException(status_code=400, detail="Show ID already in use")
    return crud.create_netflix_title(db=db, netflix_title=netflix_title)

@app.put("/netflix/titles/{show_id}", response_model=schemas.NetflixTitleResponse)
def put_netflix_title(show_id: str, netflix_title: schemas.NetflixTitlePut, db: Session = Depends(get_db)):
    db_netflix_title = crud.get_netflix_title_by_show_id(db, show_id=show_id)
    if not(db_netflix_title):
        raise HTTPException(status_code=400, detail="Netflix title not found")
    return crud.update_netflix_title(db=db, db_netflix_title=db_netflix_title, netflix_title=netflix_title)

@app.patch("/netflix/titles/{show_id}", response_model=schemas.NetflixTitleResponse)
def patch_netflix_title(show_id: str, netflix_title: schemas.NetflixTitlePatch, db: Session = Depends(get_db)):
    db_netflix_title = crud.get_netflix_title_by_show_id(db, show_id=show_id)
    if not(db_netflix_title):
        raise HTTPException(status_code=400, detail="Netflix title not found")
    return crud.partial_update_netflix_title(db=db, db_netflix_title=db_netflix_title, netflix_title=netflix_title)

# @app.post("/users/{user_id}/items/", response_model=schemas.Item)
# def create_item_for_user(
#     user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
# ):
#     return crud.create_user_item(db=db, item=item, user_id=user_id)


# @app.get("/items/", response_model=list[schemas.Item])
# def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     items = crud.get_items(db, skip=skip, limit=limit)
#     return items
