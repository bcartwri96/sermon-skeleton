# page implements the main database models.

from flask import Flask as fl
import src.scripts.index as scripts
import sqlalchemy as sa
from sqlalchemy.orm import scoped_session, sessionmaker, configure_mappers
from sqlalchemy.ext.declarative import declarative_base

# when sending to the REAL WORLD!
try:
    # i.e Heroku add-on postgres gives us the DB url to connect to right here
    # in the environment variable, but if it isn't there, then we catch the
    # exception and simply use the url we formulated earlier from development-set
    # variables
    DB_URL = scripts.get_env_variable("DATABASE_URL")
    print("Connecting to db with "+DB_URL)
except Exception:
    POSTGRES_URL = scripts.get_env_variable("POSTGRES_URL")
    POSTGRES_USER = scripts.get_env_variable("POSTGRES_USER")
    POSTGRES_PW = scripts.get_env_variable("POSTGRES_PW")
    POSTGRES_DB = scripts.get_env_variable("POSTGRES_DB")
    DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER,pw=POSTGRES_PW,url=POSTGRES_URL,db=POSTGRES_DB)


# connect
engine = sa.create_engine(DB_URL, convert_unicode=True, echo=True)
session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = session.query_property()


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

    import csv
    import bcrypt

    # let's add the admin user
    role = 1
    pw_hashed = bcrypt.hashpw('1234'.encode('utf-8'), bcrypt.gensalt(12))
    u = m.User(name="Admin", email="admin@email.com", pw=pw_hashed.decode('ascii'), role=role)
    session.add(u)

    # let's add the normal user
    role = 0
    pw_hashed = bcrypt.hashpw('5678'.encode('utf-8'), bcrypt.gensalt(12))
    u = m.User(name="User", email="user@email.com", pw=pw_hashed.decode('ascii'), role=role)
    session.add(u)

    # let's add three congregations
    n_cong = m.Congregation(name="North")
    b_cong = m.Congregation(name="Belconnen")
    c_cong = m.Congregation(name="City")
    session.add(n_cong)
    session.add(b_cong)
    session.add(c_cong)
    
    # let's add all the books of the bible
    # thanks to jpoehls @ gh.com/jpoehls/bible-metadata for the bible_meta file!
    r = 0
    with open('bible_meta.csv', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if r>0:
                b = m.Books_Bible(name=row[1], nickname=row[2], volume=row[4])
                session.add(b)
            else:
                r += 1 # first line contains junk

    session.commit()
