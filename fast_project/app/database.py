import os
import ssl

import pg8000
import sqlalchemy
from google.cloud.sql.connector import Connector

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#Sqlite config
def get_sqlite_engine():
    SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
    # SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

    sqlite_engine = create_engine(
        #check_same_thread = False only for sqlite
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    return sqlite_engine

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

# Cloud Private IP Connector - for use inside GCP as in Cloud Run instance
# Reference:
# https://cloud.google.com/sql/docs/postgres/connect-run?hl=en#private-ip
# https://github.com/GoogleCloudPlatform/python-docs-samples/blob/HEAD/cloud-sql/postgres/sqlalchemy/connect_tcp.py


# connect_tcp_socket initializes a TCP connection pool
# for a Cloud SQL instance of Postgres.
def connect_tcp_socket() -> sqlalchemy.engine.base.Engine:
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.
    db_host = os.environ["POSTGRES_HOST"]  # e.g. '127.0.0.1' ('172.17.0.1' if deployed to GAE Flex)
    db_user = os.environ["POSTGRES_USER"]  # e.g. 'my-db-user'
    db_pass = os.environ["POSTGRES_PASS"]  # e.g. 'my-db-password'
    db_name = os.environ["POSTGRES_DB"]  # e.g. 'my-database'
    db_port = os.environ["POSTGRES_PORT"]  # e.g. 5432

    connect_args = {}
    pool = sqlalchemy.create_engine(
        # Equivalent URL:
        # postgresql+pg8000://<db_user>:<db_pass>@<db_host>:<db_port>/<db_name>
        sqlalchemy.engine.url.URL.create(
            drivername="postgresql+pg8000",
            username=db_user,
            password=db_pass,
            host=db_host,
            port=db_port,
            database=db_name,
        ),
        connect_args=connect_args,
        # ...
    )
    return pool

#Cloud SQL Connector - for running locally but connecting to Cloud SQL instance
# Reference: 
# https://cloud.google.com/sql/docs/postgres/connect-connectors#python_1
# https://github.com/GoogleCloudPlatform/cloud-sql-python-connector/blob/HEAD/tests/system/test_pg8000_connection.py

# Used with GOOGLE_APPLICATION_CREDENTIALS pointing to key json file

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

db_connection_option=os.environ['DB_CONNECTION_OPTION']

if db_connection_option == 'SQLITE':
    engine = get_sqlite_engine()
elif db_connection_option == 'CLOUD_SQL_CONNECTOR':
    engine = init_connection_engine()
elif db_connection_option == 'PRIVATE_IP':
    engine = connect_tcp_socket()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()    
