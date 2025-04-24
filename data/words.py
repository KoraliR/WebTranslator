import sqlalchemy
from data.db_session import SqlAlchemyBase
from sqlalchemy import orm

class Word(SqlAlchemyBase):
    __tablename__ = "dict"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    eng = sqlalchemy.Column(sqlalchemy.String)
    ru = sqlalchemy.Column(sqlalchemy.String)
    
class UserWord(SqlAlchemyBase):
    __tablename__ = "user_words"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    word_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("dict.id"), nullable=False)

    word = orm.relationship("Word")