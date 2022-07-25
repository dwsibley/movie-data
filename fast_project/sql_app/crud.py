import hashlib
from datetime import datetime

from sqlalchemy import select, or_
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

def get_netflix_titles(db: Session, skip: int = 0, limit: int = 100, search: str = None, netflix_title_filter = None):
    #query = db.query(models.NetflixTitle).offset(skip).limit(limit).all()
    query = select(models.NetflixTitle).offset(skip).limit(limit)
    query = netflix_title_filter.filter(query)
    if search is not None:
        search = "%%%s%%" % search
        # Reference: https://stackoverflow.com/questions/7942547/using-or-in-sqlalchemy
        #search_columns = [models.NetflixTitle.title, models.NetflixTitle.description]
        #for search_col in search_columns:
        #    query = query.filter(search_col.ilike(search))
        #    query = query.filter(search_col.ilike(search))
        search_filters = [
            models.NetflixTitle.title.ilike(search),
            models.NetflixTitle.description.ilike(search),
        ]
        query = query.filter(or_(*search_filters))
    query = netflix_title_filter.sort(query)
    query = db.execute(query).scalars().all()

    return query

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

def find_or_create_netflix_country(db: Session, name: str):
    db_netflix_country = db.query(models.NetflixCountry).filter(models.NetflixCountry.name == name).first()
    if not(db_netflix_country):
        db_netflix_country = models.NetflixCountry(
            name = name,
        )
        db.add(db_netflix_country)
        db.commit()
        db.refresh(db_netflix_country)
    return db_netflix_country

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

def find_or_create_netflix_title_director_junction(db: Session, title_id: int, director_id: int):
    db_title_director_junction = db.query(models.NetflixTitleDirectorJunction).filter(models.NetflixTitleDirectorJunction.title_id == title_id).filter(models.NetflixTitleDirectorJunction.director_id == director_id).first()
    if not(db_title_director_junction):
        db_title_director_junction = models.NetflixTitleDirectorJunction(
            title_id=title_id,
            director_id=director_id
        )
        db.add(db_title_director_junction)
        db.commit()
        db.refresh(db_title_director_junction)
    return db_title_director_junction

def delete_netflix_title_director_junction(db: Session, title_id: int, director_id: int):
    #junction = db.query(models.NetflixTitleDirectorJunction).filter(models.NetflixTitleDirectorJunction.title_id == title_id).filter(models.NetflixTitleDirectorJunction.director_id == director_id).first()
    result = db.query(models.NetflixTitleDirectorJunction).filter(models.NetflixTitleDirectorJunction.title_id == title_id).filter(models.NetflixTitleDirectorJunction.director_id == director_id).delete()
    db.commit()
    return result

def create_netflix_title(db: Session, netflix_title: schemas.NetflixTitleCreate):
    # TODO: marking this function for optimization
    # create or get database directors, cast and categories for junction tables
    db_directors = [ find_or_create_netflix_name(db, director) for director in netflix_title.directors ]
    db_cast = [ find_or_create_netflix_name(db, cast_member) for cast_member in netflix_title.cast ]
    db_countries = [ find_or_create_netflix_country(db, country) for country in netflix_title.countries ]
    db_categories = [ find_or_create_netflix_category(db, category) for category in netflix_title.categories ]
    db_title_type = find_or_create_netflix_title_type(db, netflix_title.title_type)
    db_rating = find_or_create_netflix_rating(db, netflix_title.rating)
    # create title
    db_netflix_title = models.NetflixTitle(
        show_id=netflix_title.show_id,
        title=netflix_title.title,
        title_type_id=db_title_type.id,
        #title=netflix_title.title,
        #country=netflix_title.country,
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

    # create country associations in junction table
    for db_country in db_countries:
        db_title_country_junction = models.NetflixTitleCountryJunction(
            title_id=db_netflix_title.id,
            country_id=db_country.id
        )
        db.add(db_title_country_junction)
        db.commit()
        db.refresh(db_title_country_junction)

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


def update_netflix_title(db: Session, db_netflix_title: models.NetflixTitle, netflix_title: schemas.NetflixTitleCreate):
    # find title type and rating
    db_title_type = find_or_create_netflix_title_type(db, netflix_title.title_type)
    db_rating = find_or_create_netflix_rating(db, netflix_title.rating)

    # update title
    db_netflix_title.title=netflix_title.title
    db_netflix_title.title_type_id=db_title_type.id
    #db_netflix_title.date_added=datetime.strptime(netflix_title.date_added, '%B %d, %Y').date() if (netflix_title.date_added) is not None else None,
    db_netflix_title.date_added=datetime.strptime(netflix_title.date_added, '%B %d, %Y').date()
    db_netflix_title.release_year=netflix_title.release_year
    db_netflix_title.rating_id=db_rating.id
    db_netflix_title.duration=netflix_title.duration
    db_netflix_title.seasons=netflix_title.seasons
    db_netflix_title.description=netflix_title.description  
    db.commit()
    db.refresh(db_netflix_title)
    
    # if director not in directors or exists and not already associated:
    #  then create (if needed) and associate
    for director in netflix_title.directors:
        # find or create director entry
        db_director = find_or_create_netflix_name(db, director)
        # see if already associated and associate if needed
        find_or_create_netflix_title_director_junction(db, title_id=db_netflix_title.id, director_id=db_director.id)

    # if existing director not in new list (don't think order matters)
    #   then delete association
    for existing_director in db_netflix_title.directors:
        if existing_director.name not in netflix_title.directors:
            #delete association
            delete_netflix_title_director_junction(db, title_id=db_netflix_title.id, director_id=existing_director.id)

    # same thing with cast, country and categories

    #return title
    return db_netflix_title

def partial_update_netflix_title(db: Session, show_id: str, netflix_title: schemas.NetflixTitlePatch):
    pass
# def get_items(db: Session, skip: int = 0, limit: int = 100):
#     return db.query(models.Item).offset(skip).limit(limit).all()


# def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
#     db_item = models.Item(**item.dict(), owner_id=user_id)
#     db.add(db_item)
#     db.commit()
#     db.refresh(db_item)
#     return db_item
