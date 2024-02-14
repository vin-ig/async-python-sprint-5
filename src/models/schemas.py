from datetime import datetime

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Integer, String, ForeignKey, Column, DateTime
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm.decl_api import DeclarativeMeta

Base: DeclarativeMeta = declarative_base()


class User(SQLAlchemyBaseUserTable[int], Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)


class File(Base):
    __tablename__ = 'file'

    id = Column(Integer, primary_key=True)
    filename = Column(String(50), nullable=False)
    create_date = Column(DateTime, default=datetime.utcnow())
    size = Column(Integer)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'))
