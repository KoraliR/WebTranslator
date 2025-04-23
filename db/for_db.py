from data import db_session
from data.users import User
from data.words import Word
from Api import api_worker
import spacy
from data import users
nlp = spacy.load("en_core_web_sm")

#db_session.global_init("Main.db")
def search_word(word, aim_token=None, trf=None):
    session = db_session.create_session()
    if session is None:
        return False
    lemma = nlp(word)[0].lemma_
    word_obj = session.query(Word).filter(Word.eng.ilike(lemma)).first()
    if word_obj is not None:
        return word_obj.ru
    else:
        translate = api_worker.make_request_translator(word)
        add_word_to_db(lemma, translate)
        return translate
    
def get_users():
    session = db_session.create_session()
    return session.query(User.user).all()

def get_user(login):
    session = db_session.create_session()
    return session.query(users.User).filter_by(user=login).first()

def get_password(login):
    session = db_session.create_session()
    return session.query(User.password).filter(user=login)

def append_user(login, password):
    session = db_session.create_session()
    new_user = users.User(user=login)
    new_user.set_password(password)
    session.add(new_user)
    session.commit()

def add_word_to_db(lemma, ru):
    session = db_session.create_session()
    new_word = Word(eng=lemma, ru=ru)
    session.add(new_word)
    session.commit()