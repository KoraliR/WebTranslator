import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm

class User(SqlAlchemyBase):
    __tablename__ = "users"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True, autoincrement=True)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    password_hash = sqlalchemy.Column(sqlalchemy.String)
    users_words = sqlalchemy.Column(sqlalchemy.String)