from data import db_session
from data.users import User
from data.words import Word, UserWord
from data import words
from Api import api_worker
import spacy
import random
from data.words import Word as dict_model
from flask import session
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


def get_user_random_word_with_options(user_login, used_ids=None):
    session = db_session.create_session()

    user = session.query(User).filter(User.user == user_login).first()
    if not user or not user.user_words:
        return None

    user_words_list = user.user_words.split(',')

    query = session.query(Word).filter(Word.eng.in_(user_words_list))
    if used_ids:
        query = query.filter(~Word.id.in_(used_ids))
    random_word = query.order_by(func.random()).first()

    if not random_word:
        return None

    correct_translation = random_word.ru

    other_translations = session.query(Word).filter(Word.id != random_word.id).order_by(func.random()).limit(3).all()
    other_translations = [w.ru for w in other_translations]

    options = [correct_translation] + other_translations
    random.shuffle(options)

    return {
        'id': random_word.id,
        'word': random_word.eng,
        'correct_translation': correct_translation,
        'options': options
    }


def get_user_words(user_id):
    db_sess = db_session.create_session()

    user = db_sess.query(User).filter(User.id == user_id).first()
    if not user or not user.user_words:
        print("User not found or user_words is empty.")
        return []

    word_list = [word.strip() for word in user.user_words.split(',') if word.strip()]
    print("Parsed word list:", word_list)

    matched_words = db_sess.query(Word).filter(Word.eng.in_(word_list)).all()
    print("Matched Word objects from dict table:", [f"{w.eng} — {w.ru}" for w in matched_words])

    return matched_words



def get_users_words(user_id):
    db_sess = db_session.create_session()

    # Получаем пользователя
    user = db_sess.query(users.User).filter(users.User.id == user_id).first()

    # Получаем все его слова
    user_words = db_sess.query(UserWord).filter(UserWord.user_id == user_id).all()

    words = [uw.word for uw in user_words]
    return words
