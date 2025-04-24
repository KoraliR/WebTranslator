import sqlalchemy
from .db_session import SqlAlchemyBase
from sqlalchemy import orm
from werkzeug.security import generate_password_hash, check_password_hash

class User(SqlAlchemyBase):
    __tablename__ = "users"
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, unique=True, autoincrement=True)
    user = sqlalchemy.Column(sqlalchemy.String, unique=True)
    password_hash = sqlalchemy.Column(sqlalchemy.String)
    user_words = sqlalchemy.Column(sqlalchemy.String)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)