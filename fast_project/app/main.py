import os
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import DurationError, BaseModel
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

# import crud, models, schemas
# from database import SessionLocal, engine

from fastapi_filter import FilterDepends, with_prefix
from fastapi_filter.contrib.sqlalchemy import Filter

models.Base.metadata.create_all(bind=engine)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Reference: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
ALGORITHM = os.environ.get('JWT_ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRE_MINUTES'))


# fake_users_db = {
#     "johndoe": {
#         "username": "johndoe",
#         "full_name": "John Doe",
#         "email": "johndoe@example.com",
#         "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
#         "disabled": False,
#     }
# }


# class Token(BaseModel):
#     access_token: str
#     token_type: str


# class TokenData(BaseModel):
#     username: str | None = None


# class User(BaseModel):
#     username: str
#     email: str | None = None
#     full_name: str | None = None
#     disabled: bool | None = None


# class UserInDB(User):
#     hashed_password: str


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#Reference: https://fastapi.tiangolo.com/tutorial/security/first-steps/ and next section user/pass
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return schemas.UserFullDb(**user_dict)

#def authenticate_user(fake_db, username: str, password: str):
def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if not db_user:
        return False
    if not verify_password(password, db_user.password):
        return False
    return db_user


def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    #user = get_user(fake_users_db, username=token_data.username)
    db_user = crud.get_user_by_username(db, username=token_data.username)
    if db_user is None:
        raise credentials_exception
    return db_user

async def get_current_active_user(current_user: schemas.UserResponse = Depends(get_current_user)):
    if not(current_user.is_active):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(username=form_data.username, password=form_data.password, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=schemas.UserResponse)
async def read_users_me(current_user: schemas.UserResponse = Depends(get_current_active_user)):
    return current_user


# @app.get("/users/me/items/")
# async def read_own_items(current_user: User = Depends(get_current_active_user)):
#     return [{"item_id": "Foo", "owner": current_user.username}]

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


# End points 
@app.post("/users/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# @app.get("/users/", response_model=list[schemas.UserResponse])
# def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
#     users = crud.get_users(db, skip=skip, limit=limit)
#     return users

# @app.get("/users/{user_id}", response_model=schemas.UserResponse)
# def read_user(user_id: int, db: Session = Depends(get_db)):
#     db_user = crud.get_user(db, user_id=user_id)
#     if db_user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return db_user

@app.get("/netflix/titles/", response_model=list[schemas.NetflixTitleResponse])
#def read_netflix_titles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
def read_netflix_titles(netflix_title_filter: NetflixTitleFilter = FilterDepends(NetflixTitleFilter), skip: int = 0, limit: int = 100, search: str = None, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    netflix_titles = crud.get_netflix_titles(db, skip=skip, limit=limit, search=search, netflix_title_filter=netflix_title_filter)
    return netflix_titles

@app.get("/netflix/titles/{show_id}", response_model=schemas.NetflixTitleResponse)
def read_netflix_title(show_id: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):

    netflix_title = crud.get_netflix_title_by_show_id(db, show_id=show_id)
    if netflix_title is None:
        raise HTTPException(status_code=404, detail="Netflix title not found")
    return netflix_title

@app.post("/netflix/titles/", response_model=schemas.NetflixTitleResponse)
def create_netflix_title(netflix_title: schemas.NetflixTitleCreate, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_netflix_title = crud.get_netflix_title_by_show_id(db, show_id=netflix_title.show_id)
    if db_netflix_title:
        raise HTTPException(status_code=400, detail="Show ID already in use")
    return crud.create_netflix_title(db=db, netflix_title=netflix_title)

@app.put("/netflix/titles/{show_id}", response_model=schemas.NetflixTitleResponse)
def put_netflix_title(show_id: str, netflix_title: schemas.NetflixTitlePut, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_netflix_title = crud.get_netflix_title_by_show_id(db, show_id=show_id)
    if not(db_netflix_title):
        raise HTTPException(status_code=400, detail="Netflix title not found")
    return crud.update_netflix_title(db=db, db_netflix_title=db_netflix_title, netflix_title=netflix_title)

@app.patch("/netflix/titles/{show_id}", response_model=schemas.NetflixTitleResponse)
def patch_netflix_title(show_id: str, netflix_title: schemas.NetflixTitlePatch, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
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
