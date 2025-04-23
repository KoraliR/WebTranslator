from data import db_session
from data.users import User
from data.words import Word
from Api import api_worker
import spacy
import random
from data import users
from sqlalchemy.sql import func  # Импортируем func

nlp = spacy.load("en_core_web_sm")

# db_session.global_init("Main.db")

def search_word(word, aim_token=None, trf=None):
    session = db_session.create_session()
    if session is None:
        return False
    lemma = nlp(word)[0].lemma_
    word_obj = session.query(Word).filter(Word.eng.ilike(lemma)).first()
    if word_obj is not None:
        return word_obj.ru
    else:
        return api_worker.make_request_translator(word)

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
    return session.query(User.password).filter_by(user=login).first()

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

def get_random_word_with_options(used_ids=None):
    session = db_session.create_session()

    query = session.query(Word)
    if used_ids:
        query = query.filter(~Word.id.in_(used_ids))
    random_word = query.order_by(func.random()).first()

    if not random_word:
        return None

    correct_translation = random_word.ru

    # Получаем три случайных других перевода
    other_translations = session.query(Word).filter(Word.id != random_word.id).order_by(func.random()).limit(3).all()
    other_translations = [word.ru for word in other_translations]

    options = [correct_translation] + other_translations
    random.shuffle(options)

    return {
        'id': random_word.id,
        'word': random_word.eng,
        'correct_translation': correct_translation,
        'options': options
    }
