from datetime import datetime

from sqlalchemy import Integer, String, TIMESTAMP, ForeignKey, Column, Boolean, JSON
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta

Base: DeclarativeMeta = declarative_base()


# class User(Base):
#     __tablename__ = 'user'
#     id = Column(Integer, primary_key=True)
#     name = Column(String(50), nullable=False)
#     email = Column(String(50), unique=True, nullable=False)
#     password = Column(String(50))

#
# class TransitionSchema(Base):
#     __tablename__ = 'transition'
#     id = Column(Integer, primary_key=True)
#     click_date = Column(TIMESTAMP, default=datetime.utcnow)
#     url_id = Column(Integer, ForeignKey('short_url.id', ondelete='CASCADE'))
#     client_info = Column(JSON)
