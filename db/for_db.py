from data import db_session
from data.users import User
from data.words import Word
from Api import api_worker
import spacy
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
        return api_worker.make_request_translator(word)