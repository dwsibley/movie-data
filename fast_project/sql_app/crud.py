import hashlib
from datetime import datetime

from sqlalchemy.orm import Session

from . import models, schemas


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    db_user = models.User(email=user.email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_netflix_title_by_show_id(db: Session, show_id: str):
    return db.query(models.NetflixTitle).filter(models.NetflixTitle.show_id == show_id).first()

def find_or_create_netflix_name(db: Session, name: str):
    db_netflix_name = db.query(models.NetflixName).filter(models.NetflixName.name == name).first()
    if not(db_netflix_name):
        db_netflix_name = models.NetflixName(
            name = name,
        )
        db.add(db_netflix_name)
        db.commit()
        db.refresh(db_netflix_name)
    return db_netflix_name

def find_or_create_netflix_category(db: Session, name: str):
    db_netflix_category = db.query(models.NetflixCategory).filter(models.NetflixCategory.name == name).first()
    if not(db_netflix_category):
        db_netflix_category = models.NetflixCategory(
            name = name,
        )
        db.add(db_netflix_category)
        db.commit()
        db.refresh(db_netflix_category)
    return db_netflix_category

def find_or_create_netflix_title_type(db: Session, name: str):
    db_netflix_title_type = db.query(models.NetflixTitleType).filter(models.NetflixTitleType.name == name).first()
    if not(db_netflix_title_type):
        db_netflix_title_type = models.NetflixTitleType(
            name = name,
        )
        db.add(db_netflix_title_type)
        db.commit()
        db.refresh(db_netflix_title_type)
    return db_netflix_title_type

def find_or_create_netflix_rating(db: Session, name: str):
    db_netflix_rating = db.query(models.NetflixRating).filter(models.NetflixRating.name == name).first()
    if not(db_netflix_rating):
        db_netflix_rating = models.NetflixRating(
            name = name,
        )
        db.add(db_netflix_rating)
        db.commit()
        db.refresh(db_netflix_rating)
    return db_netflix_rating

def create_netflix_title(db: Session, netflix_title: schemas.NetflixTitleCreate):
    # create or get database directors, cast and categories for junction tables
    db_directors = [ find_or_create_netflix_name(db, director) for director in netflix_title.directors ]
    db_cast = [ find_or_create_netflix_name(db, cast_member) for cast_member in netflix_title.cast ]
    db_categories = [ find_or_create_netflix_category(db, category) for category in netflix_title.categories ]
    db_title_type = find_or_create_netflix_title_type(db, netflix_title.title_type)
    db_rating = find_or_create_netflix_rating(db, netflix_title.rating)
    # create title
    db_netflix_title = models.NetflixTitle(
        show_id=netflix_title.show_id,
        title=netflix_title.title,
        title_type_id=db_title_type.id,
        #title=netflix_title.title,
        country=netflix_title.country,
        #example date_added: March 15, 2017
        date_added=datetime.strptime(netflix_title.date_added, '%B %d, %Y') if (netflix_title.date_added) is not None else None,
        release_year=netflix_title.release_year,
        #rating=netflix_title.rating,
        rating_id=db_rating.id,
        duration=netflix_title.duration,
        seasons=netflix_title.seasons,
        description=netflix_title.description
    )
    db.add(db_netflix_title)
    db.commit()
    db.refresh(db_netflix_title)
    
    # create director associations in junction table
    for db_director in db_directors:
        db_title_director_junction = models.NetflixTitleDirectorJunction(
            title_id=db_netflix_title.id,
            director_id=db_director.id
        )
        db.add(db_title_director_junction)
        db.commit()
        db.refresh(db_title_director_junction)

    # create cast associations in junction table
    for db_cast_member in db_cast:
        db_title_cast_junction = models.NetflixTitleCastJunction(
            title_id=db_netflix_title.id,
            cast_id=db_cast_member.id
        )
        db.add(db_title_cast_junction)
        db.commit()
        db.refresh(db_title_cast_junction)

    # create category associations in junction table
    for db_category in db_categories:
        db_title_category_junction = models.NetflixTitleCategoryJunction(
            title_id=db_netflix_title.id,
            category_id=db_category.id
        )
        db.add(db_title_category_junction)
        db.commit()
        db.refresh(db_title_category_junction)

    #return title
    return db_netflix_title

# def get_items(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Item).offset(skip).limit(limit).all()


# def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
#     db_item = models.Item(**item.dict(), owner_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item
