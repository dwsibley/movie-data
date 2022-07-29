import datetime
from logging.handlers import RotatingFileHandler
#from msilib.schema import Directory
from uuid import UUID
import enum
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Date, Enum
#from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .database import Base
# from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    #uuid = Column(UUID, unique=True, index=True, as_uuid=True) # see if making this primary key impacts performance
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String) # save hashed at least
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    #items = relationship("Item", back_populates="owner")


# class Item(Base):
#     __tablename__ = "items"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     description = Column(String, index=True)
#     owner_id = Column(Integer, ForeignKey("users.id"))

#     owner = relationship("User", back_populates="items")

# reference: https://docs.sqlalchemy.org/en/14/core/type_basics.html
# reference: https://medium.com/the-andela-way/how-to-create-django-like-choices-field-in-flask-sqlalchemy-1ca0e3a3af9d

# class NetflixTypeEnum(enum.Enum):
#     movie = 'Movie'
#     tv_show = 'TV Show'

# class NetflixRatingEnum(enum.Enum):
#     pg_13 = 'PG-13'
#     tv_ma = 'TV-MA'
#     pg = 'PG'
#     tv_14 = 'TV-14'
#     tv_pg = 'TV-PG'
#     tv_y = 'TV-Y'
#     tv_y7 = 'TV-Y7'
#     r = 'R'
#     tv_g = 'TV-G'
#     g = 'G'
#     nc_17 = 'NC-17'
#     nr = 'NR'
#     tv_y7_fv = 'TV-Y7-FV'
#     ur = 'UR'

# connection.execute(t.insert(), {"value": MyEnum.two})
# assert connection.scalar(t.select()) is MyEnum.two

class NetflixTitleType(Base):
    __tablename__ = "netflix_title_types"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class NetflixRating(Base):
    __tablename__ = "netflix_ratings"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class NetflixTitle(Base):
    __tablename__ = "netflix_titles"

    #show_id,type,title,director,cast,country,date_added,release_year,rating,duration,listed_in,description

    id = Column(Integer, primary_key=True, index=True)
    #uuid = Column(UUID, unique=True, index=True, as_uuid=True) # see if making this primary key impacts performance
    show_id = Column(String, unique=True, index=True)
    #title_type = Column(Enum(NetflixTypeEnum)) # choices Movie, TV Show
    title_type_id = Column(Integer, ForeignKey("netflix_title_types.id"))
    title = Column(String, index=True)
    #director = Column(String, index=True) # consider another table, consider list field, 
    #cast
    #country = Column(String, index=True)
    date_added = Column(Date)
    release_year = Column(Integer)
    #rating = Column(Enum(NetflixRatingEnum))
    rating_id = Column(Integer, ForeignKey("netflix_ratings.id"))
    duration = Column(Integer)
    seasons = Column(Integer)
    #listed_in    #many to many relationship for genres or categories
    description = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    #Reference: https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#relationships-many-to-many
    directors = relationship("NetflixName", secondary="netflix_title_director_junction")
    cast = relationship("NetflixName", secondary="netflix_title_cast_junction")
    countries = relationship("NetflixCountry", secondary="netflix_title_country_junction")
    categories = relationship("NetflixCategory", secondary="netflix_title_category_junction")
    _title_type = relationship("NetflixTitleType")   #Reference: https://stackoverflow.com/questions/31439394/sqlalchemy-select-data-associated-with-foreign-key-not-the-foreign-key-itself
    _rating = relationship("NetflixRating")

    @property
    def title_type(self):
        return self._title_type.name

    @property
    def rating(self):
        return self._rating.name

class NetflixName(Base):
    __tablename__ = "netflix_names"

    #NOTE: at this point not addressing aliases (same person with multiple names)
    #      which is also why this is a "names" table not a "people" table

    id = Column(Integer, primary_key=True, index=True)
    #uuid = Column(UUID, unique=True, index=True, as_uuid=True) # see if making this primary key impacts performance
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # def __str__(self):  # seeing if this will help with response if wanted a simple list of strings - s
    #     return self.name  

class NetflixTitleDirectorJunction(Base):
    __tablename__ = "netflix_title_director_junction"

    id = Column(Integer, primary_key=True, index=True)
    #uuid = Column(UUID, unique=True, index=True, as_uuid=True) # see if making this primary key impacts performance
    title_id = Column(Integer, ForeignKey("netflix_titles.id"))
    director_id = Column(Integer, ForeignKey("netflix_names.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class NetflixTitleCastJunction(Base):
    __tablename__ = "netflix_title_cast_junction"

    id = Column(Integer, primary_key=True, index=True)
    #uuid = Column(UUID, unique=True, index=True, as_uuid=True) # see if making this primary key impacts performance
    title_id = Column(Integer, ForeignKey("netflix_titles.id"))
    cast_id = Column(Integer, ForeignKey("netflix_names.id"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class NetflixCountry(Base):
    __tablename__ = "netflix_countries"

    id = Column(Integer, primary_key=True, index=True)
    #uuid = Column(UUID, unique=True, index=True, as_uuid=True) # see if making this primary key impacts performance
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class NetflixTitleCountryJunction(Base):
    __tablename__ = "netflix_title_country_junction"

    id = Column(Integer, primary_key=True, index=True)
    #uuid = Column(UUID, unique=True, index=True, as_uuid=True) # see if making this primary key impacts performance
    title_id = Column(Integer, ForeignKey("netflix_titles.id"))
    country_id = Column(Integer, ForeignKey("netflix_countries.id"))    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class NetflixCategory(Base):
    __tablename__ = "netflix_categories"

    id = Column(Integer, primary_key=True, index=True)
    #uuid = Column(UUID, unique=True, index=True, as_uuid=True) # see if making this primary key impacts performance
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class NetflixTitleCategoryJunction(Base):
    __tablename__ = "netflix_title_category_junction"

    id = Column(Integer, primary_key=True, index=True)
    #uuid = Column(UUID, unique=True, index=True, as_uuid=True) # see if making this primary key impacts performance
    title_id = Column(Integer, ForeignKey("netflix_titles.id"))
    category_id = Column(Integer, ForeignKey("netflix_categories.id"))    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
