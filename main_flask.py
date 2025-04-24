from flask import Flask
from flask import render_template, request, flash, redirect, session, url_for

import Api.make_tokens
from db import for_db
from data import db_session, users,words
from string import ascii_letters
from string import punctuation
import re
from data.words import UserWord, Word
from data.users import User
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


app = Flask(__name__)
app.secret_key = 'supersecretkey'


def check_word(word):
    if len(word) < 2:
        return (False, "less_2")
    if not all(x in ascii_letters for x in word):
        return (False, "not_char")
    if not all(x in punctuation for x in word):
        return (True, True)
    else:
        return (False, "punct")

def check_login_and_password_auth(login, password):
    user1 = for_db.get_user(login)
    if not user1:
        return(False, 'unexist')
    elif not user1.check_password(password):
        return(False, 'uncor_pass')
    else:
        return(True, True)

def check_login_and_password_reg(login, password, password1):
    a = [''.join(list(a)) for a in for_db.get_users()]
    if login in a:
        return(False, 'taken')
    elif len(login) < 2:
        return(False, 'too_short_log')
    elif len(password) < 8:
        return(False, 'too_short')
    elif not re.search(r'\d', password):
        return (False, 'no_digit')
    elif not re.search(r'[a-zA-Z]', password):
        return (False, 'no_alpha')
    elif password != password1:
        return(False, 'diffrent')
    else:
        return(True, True)
    
@app.before_request
def set_default_theme():
    global flag_registration
    global login
    if "theme" not in session:
        session["theme"] = "light"
    if "flag_registration" not in session:
        session["flag_registration"] = False
        session["login"] = ""


@app.route("/")
def hi_page():
    flag_registration = session.get("flag_registration")
    login = session.get("login")
    theme = session.get("theme")
    print(flag_registration)
    return render_template("start.html", flag_registration=flag_registration, theme=theme, login=login)

# @app.route("/account")
# def login_page():
#     flag_registration = session.get("flag_registration")
#     login = session.get("login")
#     id = session.get("id")
#     print(login, id)
#     theme = session.get("theme")
#     words = for_db.get_users_words()
#     return render_template("account.html", user_id=id, flag_registration=flag_registration, theme=theme, username=login, words=words)



@app.route("/account")
def account():
    theme = session.get("theme", "light")
    flag_registration = session.get("flag_registration", False)
    user_id = session.get("user_id")
    login = session.get("login", "")

    print("Account page — session user_id:", user_id)

    if not user_id:
        return redirect("/log_in")

    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)

    user_word_list = []
    if user.user_words:
        word_engs = [w.strip() for w in user.user_words.split(',') if w.strip()]
        words = db_sess.query(Word).filter(Word.eng.in_(word_engs)).all()
        user_word_list = words

    return render_template(
        "account.html",
        theme=theme,
        flag_registration=flag_registration,
        user_words=user_word_list,
        user_id=user.id,
        login=user.user
    )

@app.route('/delete_word', methods=['POST'])
def delete_word():
    user_id = session.get("user_id")
    if not user_id:
        return redirect('/log_in')

    word_eng = request.form.get('word_eng')
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)

    if user and user.user_words:
        word_list = [w.strip() for w in user.user_words.split(',') if w.strip()]
        if word_eng in word_list:
            word_list.remove(word_eng)
            user.user_words = ",".join(word_list)
            db_sess.commit()

    return redirect('/account')



@app.route('/delete_account')
def delete_account():
    if not session.get('flag_registration'):
        return redirect('/log_in')

    user_login = session.get('login')
    db_sess = db_session.create_session()
    user = db_sess.query(users.User).filter(users.User.user == user_login).first()

    if user:
        # Удалим связанные данные, если нужно (например, слова, если есть привязка)
        db_sess.delete(user)
        db_sess.commit()

    session.clear()
    return redirect('/log_in')

@app.route("/logout")
def logout():
    session.clear()  # очищает все данные из сессии
    return redirect("/")



@app.route("/learning")
def learning():
    flag_registration = session.get("flag_registration")
    login = session.get("login")
    theme = session.get("theme")

    if not flag_registration or not login:
        return render_template("learning.html", not_logged_in=True, theme=theme)

    words_list = []
    used_ids = set()
    for _ in range(10):
        word_data = for_db.get_user_random_word_with_options(login, used_ids)
        if word_data:
            used_ids.add(word_data['id'])
            words_list.append(word_data)

    return render_template("learning.html",
                           words=words_list,
                           flag_registration=flag_registration,
                           login=login,
                           theme=theme,
                           not_logged_in=False)




@app.route("/registration", methods=['POST', 'GET'])
def registration_page():
    theme = session.get("theme")
    if request.method == "POST":
        login = request.form["login"]
        password = request.form['password']
        password1 = request.form['password1']

        result_check_login_and_password_r = check_login_and_password_reg(login, password, password1)
        if result_check_login_and_password_r[0]:
            for_db.append_user(login, password)
            session["flag_registration"] = True
            session["login"] = login

            # получить user_id после добавления
            db_sess = db_session.create_session()
            user = db_sess.query(users.User).filter(users.User.user == login).first()
            if user:
                session["user_id"] = user.id

            return redirect(url_for("hi_page"))
        else:
            return render_template("registration.html",
                                   error_flag=True,
                                   flag_registration=False,
                                   error_code=result_check_login_and_password_r[-1],
                                   theme=theme,
                                   login=login)
    
    if session.get("flag_registration"):
        return redirect(url_for("hi_page"))
    return render_template("registration.html", theme=theme, flag_registration=False, login=None)

@app.route("/log_in", methods=['POST', 'GET'])
def log_in():
    theme = session.get("theme")
    if request.method == "POST":
        login = request.form["login"]
        password = request.form["password"]

        result = check_login_and_password_auth(login, password)

        if result[0]:  # Успешная авторизация
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.user == login).first()

            if user:
                session["flag_registration"] = True
                session["login"] = login
                session["user_id"] = user.id  # <<< ВАЖНО
                print("✅ Установлен user_id:", user.id)
                return redirect("/account")
            else:
                print("❌ Пользователь не найден в БД")
                return render_template("log_in.html", error_flag=True, error_code="Пользователь не найден", theme=theme)

        else:
            return render_template("log_in.html", error_flag=True, error_code=result[-1], theme=theme)

    return render_template("log_in.html", theme=theme)

@app.route("/translate", methods=['POST', 'GET'])
def translate():
    flag_registration = session.get("flag_registration")
    login = session.get("login")
    theme = session.get("theme")
    if request.method == "POST":
        text = request.form["word"]
        result_check_word = check_word(text)
        if result_check_word[0]:
            translate = for_db.search_word(text)
            return render_template("translator.html", flag_registration=flag_registration, flag_translated=True, translated_text=translate, theme=theme, login=login, word=text)
        else:
            return render_template("translator.html", flag_registration=flag_registration, error_flag=True, login=login, error_code=result_check_word[-1], theme=theme)
    return render_template("translator.html", flag_registration=flag_registration, login=login, theme=theme)
#error_flag, error_code, flag_translated, translated_text
@app.route("/test")
def test():
    return render_template("test.html", theme="dark")

# @app.route("/test2")
# def test2():
#     return render_template("test.html", theme="light")
#
@app.route("/toggle_theme", methods=["POST"])
def toggle_theme():
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    elif current_theme == "light":
        session["theme"] = "dark"
    return redirect(request.referrer or url_for(hi_page))


@app.route('/add_to_dictionary', methods=["POST"])
def add_to_dict():
    flag_registration = session.get("flag_registration")
    login = session.get("login")
    eng_word = request.form["word"]
    theme = session.get("theme")
    translation = request.form["translation"]
    if flag_registration:
        flag_word = for_db.add_word_user_dict(login, eng_word)
        if flag_word:
            return render_template("translator.html", flag_registration=flag_registration, flag_translated=True, translated_text=translation, theme=theme, login=login, word=eng_word, word_added=True)
        else:
            return render_template("translator.html", flag_registration=flag_registration, flag_translated=True,
                                   translated_text=translation, theme=theme, login=login, word=eng_word, word_exists=True)
    return redirect(url_for(translate()))




if __name__ == "__main__":
    expire_at = Api.make_tokens.start_make_token()
    db_session.global_init("db/Main.db")
    app.run(port=8080, host="127.0.0.1")
