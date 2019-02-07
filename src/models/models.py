from src.models.db import Base as Base
from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

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
    # NOTE in prod, media_url and pod_id need to be unique. enforcable at db
    __tablename__ = 'sermons'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True)
    title = Column(String(250), unique=True)
    tmp_thumbnail = Column(String(250))
    tmp_media = Column(String(250))
    pod_id = Column(String(100))
    pod_media_url = Column(String(100))
    pod_logo_url = Column(String(100))
    date_given = Column(Date)
    sermon_series_id = Column(Integer, ForeignKey("sermon_series.id"))
    sermon_series = relationship("Sermon_Series")


    def __init__(self, title=None, tmp_thumbnail=None, tmp_media=None, date_given=None, pod_id=None, pod_media_url=None, pod_logo_url=None):
        self.title = title
        self.tmp_thumbnail = tmp_thumbnail
        self.tmp_media = tmp_media
        self.pod_id = pod_id
        self.pod_media_url = pod_media_url
        self.pod_logo_url = pod_logo_url
        self.date_given = date_given

class Sermon_Series(Base):
    __tablename__ = 'sermon_series'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))

    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name
