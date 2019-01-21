from src.models.db import Base as Base
from sqlalchemy import Column, Integer, String

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    pw = Column(String(120), nullable=False)

    def __init__(self, name=None, email=None, pw=None):
        self.name = name
        self.email = email
        self.pw = pw

    def __repr__(self):
        return '<User %r>' % (self.pw)

    def is_active(self):
        return self._user.enabled

    def is_authenticated(self):
        return True

    def is_admin(self):
        if is_authenticated:
            return True
        else:
            return False

    def get_id(self):
        # note this is unicode, because python3 is by default.
        return self.id


class Sermons(Base):
    __tablename__ = 'sermons'
    id = Column(Integer, primary_key=True)
    file_loc = Column(String(250), unique=True)
    thumbnail = Column(String(250))

    def __init__(self, file_loc=None):
        self.file_loc = file_loc
        self.thumbnail = thumbnail
