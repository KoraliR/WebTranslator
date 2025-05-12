from data import db_session
from flask_login import current_user
from data.users import User
from data.words import Word
from data import words
from Api import api_worker
import spacy
import random
from data.words import Word
from sqlalchemy.sql import func  

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

def add_word_to_db(lemma, ru):
    session = db_session.create_session()
    new_word = Word(eng=lemma, ru=ru)
    session.add(new_word)
    session.commit()

def get_user_random_word_with_options():
    result = []
    session = db_session.create_session()
    user =  current_user
    if not user.user_words:
        return []
    user_word_list = [w for w in user.user_words.strip(",").split(",") if w]
    if len(user_word_list) < 4:
        return []
    random.shuffle(user_word_list)
    for i in user_word_list:
        random_word_eng = i
        word_obj = session.query(Word).filter_by(eng=random_word_eng).first()
        correct_translation = word_obj.ru
        other_word_objs = session.query(Word).filter(Word.eng.in_(user_word_list), Word.eng != random_word_eng).all()
        other_translations = [w.ru for w in other_word_objs]
        extra_translations = (
            session.query(Word)
            .filter(~Word.eng.in_([random_word_eng] + user_word_list))
            .order_by(func.random())
            .limit(3 - len(other_translations))
            .all()
            )
        other_translations += [w.ru for w in extra_translations]
        other_translations = other_translations[:3]
        options = [correct_translation] + other_translations
        random.shuffle(options)
        result.append({
            'id': word_obj.eng,
            'word': word_obj.eng,
            'correct_translation': correct_translation,
            'options': options
        })
    return result

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

