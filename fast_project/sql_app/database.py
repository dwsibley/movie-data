import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#Sqlite config
# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# # SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

# engine = create_engine(
#     #check_same_thread = False only for sqlite
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
# )

#Postgres Config
user = os.environ.get('POSTGRES_DB_USER')
password = os.environ.get('POSTGRES_DB_PASSWORD')
server = os.environ.get('POSTGRES_DB_SERVER')
db_name = os.environ.get('POSTGRES_DB_NAME')
#SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
SQLALCHEMY_DATABASE_URL = "postgresql://%s:%s@%s/%s" % (user, password, server, db_name)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
