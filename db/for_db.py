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


def get_user_random_word_with_options(login, used_words=None):
    session = db_session.create_session()
    user = session.query(User).filter(User.user == login).first()

    if not user or not user.user_words:
        return None

    user_word_list = user.user_words.strip(",").split(",")
    user_word_list = [word for word in user_word_list if word]  # удаляем пустые

    if used_words:
        user_word_list = [w for w in user_word_list if w not in used_words]

    if len(user_word_list) < 1:
        return None

    random_word_eng = random.choice(user_word_list)
    word_obj = session.query(Word).filter(Word.eng == random_word_eng).first()

    if not word_obj:
        return None

    correct_translation = word_obj.ru

    # Получаем другие слова пользователя для опций
    other_words = [w for w in user.user_words.strip(",").split(",") if w != random_word_eng]
    other_word_objs = session.query(Word).filter(Word.eng.in_(other_words)).all()
    other_translations = [w.ru for w in other_word_objs]

    # Если других слов меньше трёх — досыпаем из всех слов, но исключаем текущий
    if len(other_translations) < 3:
        needed = 3 - len(other_translations)
        extra_translations = (
            session.query(Word)
            .filter(~Word.eng.in_([random_word_eng] + other_words))
            .order_by(func.random())
            .limit(needed)
            .all()
        )
        other_translations += [w.ru for w in extra_translations]

    # Берём только 3 опции и мешаем с правильным
    other_translations = other_translations[:3]
    options = [correct_translation] + other_translations
    random.shuffle(options)

    return {
        'id': word_obj.eng,
        'word': word_obj.eng,
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

def get_word_id(word):
    session = db_session.create_session()
    word_id = session.query(Word.id).filter(Word.eng == word).first()
    return word_id


def add_word_user_dict(login, word):
    session = db_session.create_session()
    user = session.query(User).filter(User.user == login).first()
    if user.user_words is None:
        user.user_words = word + ","
    else:
        user_list = user.user_words.split(",")[:-1]
        if word in user_list:
            return False
        else:
            user_list.append(word)
            user.user_words = ",".join(user_list) + ","
    session.commit()
    return True

