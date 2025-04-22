import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm

class Word(SqlAlchemyBase):
    __tablename__ = "dict"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    eng = sqlalchemy.Column(sqlalchemy.String)
    ru = sqlalchemy.Column(sqlalchemy.String)