import os

import pg8000
import sqlalchemy
from google.cloud.sql.connector import Connector

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
# user = os.environ.get('POSTGRES_DB_USER')
# password = os.environ.get('POSTGRES_DB_PASSWORD')
# server = os.environ.get('POSTGRES_DB_SERVER')
# db_name = os.environ.get('POSTGRES_DB_NAME')
# #SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"
# SQLALCHEMY_DATABASE_URL = "postgresql://%s:%s@%s/%s" % (user, password, server, db_name)

# engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base() 


# The Cloud SQL Python Connector can be used along with SQLAlchemy using the
# 'creator' argument to 'create_engine'
def init_connection_engine() -> sqlalchemy.engine.Engine:
    def getconn() -> pg8000.dbapi.Connection:
        # initialize Connector object for connections to Cloud SQL
        with Connector() as connector:
            conn: pg8000.dbapi.Connection = connector.connect(
                os.environ["POSTGRES_CONNECTION_NAME"],
                "pg8000",
                user=os.environ["POSTGRES_USER"],
                password=os.environ["POSTGRES_PASS"],
                db=os.environ["POSTGRES_DB"],
            )
            return conn

    # create SQLAlchemy connection pool
    pool = sqlalchemy.create_engine(
        "postgresql+pg8000://",
        creator=getconn,
    )
    pool.dialect.description_encoding = None
    return pool

engine = init_connection_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()    
