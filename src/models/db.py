# page implements the main database models.

from flask import Flask as fl
import src.scripts.index as scripts
import sqlalchemy as sa
from sqlalchemy.orm import scoped_session, sessionmaker, configure_mappers
from sqlalchemy.ext.declarative import declarative_base

# the values of those depend on your setup
POSTGRES_URL = scripts.get_env_variable("POSTGRES_URL")
POSTGRES_USER = scripts.get_env_variable("POSTGRES_USER")
POSTGRES_PW = scripts.get_env_variable("POSTGRES_PW")
POSTGRES_DB = scripts.get_env_variable("POSTGRES_DB")
DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)

# when sending to the REAL WORLD!
try:
    DATABASE_URL = scripts.index.get_env_variable("DATABASE_URL")
    DB_URL = DATABASE_URL
except Exception:
    pass

# connect
engine = sa.create_engine(DB_URL, convert_unicode=True)
session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = session.query_property()

configure_mappers()


def create_db():
    """Destroys and creates the database and tables"""
    from sqlalchemy_utils import database_exists, create_database, drop_database
    if not database_exists(DB_URL):
        print('Creating database.')
        create_database(DB_URL)
    else:
        drop_database(DB_URL)
        create_database(DB_URL)
        print("Deleted and created new database")
        create_tables()

def reset_db():
    """Destroys and creates the database + tables."""

    metadata = sa.MetaData()
    metadata.reflect(engine)
    for tbl in reversed(metadata.sorted_tables):
        tbl.drop(engine)
    create_tables()

def create_tables():
    """Works the models into the db in using the ORM"""
    print('Creating tables.')
    # import the models used to describe the tables we're creating (using the
    # ORM). Link: http://flask-sqlalchemy.pocoo.org/2.3/models/
    import src.models.models as m
    Base.metadata.create_all(bind=engine)
    session.commit()

    # let's add the admin user
    u = m.User(name="Admin", email="admin", pw="1234")
    session.add(u)
    session.commit()
