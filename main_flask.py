from flask import Flask
from flask import render_template, request, flash, redirect, session, url_for
from flask_login import login_user, logout_user, login_required, current_user
from data.RegForm import RegForm
import Api.make_tokens
from db import for_db
from data import db_session, users
from string import ascii_letters
from string import punctuation
import re
from data.words import Word
from data.users import User
from flask_sqlalchemy import SQLAlchemy
import os
import json
import datetime
import time
import threading
from flask_login import LoginManager
from data.LoginForm import LoginForm
db = SQLAlchemy()


app = Flask(__name__)
app.secret_key = 'supersecretkey'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.get(User, int(user_id))

def monitor_token():
    while True:
        if not os.path.exists(os.path.join(os.getcwd(), "Api", "aim_tokens", "aim_token_trans.json")):
            Api.make_tokens.start_make_token()
            time.sleep(10)
        try:
            path = os.path.join(os.getcwd(), "Api", "aim_tokens", "aim_token_trans.json")
            with open(path, "r") as f:
                obj = json.loads(f.read())
                expire_str = obj["expiresAt"].split("T")
                expire_date = expire_str[0].split("-")
                expire_time = expire_str[1].split(":")
                now = datetime.datetime.now()
                year = int(expire_date[0])
                month = int(expire_date[1])
                day = int(expire_date[2])
                h = int(expire_time[0])
                m = int(expire_time[1]) - 1
                expire_date = datetime.datetime(year=year, month=month, day=day, hour=h, minute=m)
                time_delta = expire_date - now
                time_delta = time_delta.total_seconds()
                if time_delta < 300:
                    Api.make_tokens.start_make_token(flag=True)


        except Exception as e:
            print("Ошибка при проверке токена:", e)
        time.sleep(120)



def check_word(word):
    if len(word) < 2:
        return (False, "less_2")
    if not all(x in ascii_letters for x in word):
        return (False, "not_char")
    if not all(x in punctuation for x in word):
        return (True, True)
    else:
        return (False, "punct")
    
@app.before_request
def set_default_theme():
    if "theme" not in session:
        session["theme"] = "light"

@app.route("/")
def hi_page():
    theme = session.get("theme")
    return render_template("start.html", theme=theme)

@app.route("/account")
def account():
    theme = session.get("theme", "light")
    db_sess = db_session.create_session()
    user = current_user
    user_word_list = []
    if user.user_words:
        word_engs = [w.strip() for w in user.user_words.split(',') if w.strip()]
        words = db_sess.query(Word).filter(Word.eng.in_(word_engs)).all()
        user_word_list = words
    return render_template(
        "account.html",
        theme=theme,
        user_words=user_word_list)

@app.route('/delete_word', methods=['POST'])
def delete_word():
    word_eng = request.form.get('word_eng')
    db_sess = db_session.create_session()
    user = current_user
    if user and user.user_words:
        word_list = [w.strip() for w in user.user_words.split(',') if w.strip()]
        if word_eng in word_list:
            word_list.remove(word_eng)
            user.user_words = ",".join(word_list)
            db_sess.commit()
    return redirect('/account')

@app.route('/delete_account')
def delete_account():
    db_sess = db_session.create_session()
    user = db_sess.query(users.User).filter(users.User.user == current_user.user).first()
    if user:
        db_sess.delete(user)
        db_sess.commit()
    logout_user()
    session.clear()
    return redirect('/login')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route("/learning")
@login_required
def learning():
    theme = session.get("theme")
    words_list = for_db.get_user_random_word_with_options()
    return render_template("learning.html",
                           words=words_list,
                           theme=theme)

@app.route("/registration", methods=['POST', 'GET'])
def registration_page():
    theme = session.get("theme")
    form = RegForm()

    if request.method == 'POST':
        if form.validate():
            db_sess = db_session.create_session()
            existing_user = db_sess.query(User).filter(User.user == form.user.data).first()
            if existing_user:
                flash("Пользователь с таким именем уже существует.", "error")
                return render_template("registration.html", theme=theme, form=form)
            else:
                user = User(user=form.user.data)
                user.set_password(form.password.data)
                db_sess.add(user)
                db_sess.commit()
                login_user(user, remember=form.remember_me.data)
                flash('Вы успешно зарегистрировались', 'success')
                return redirect('/')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    if field == 'user':
                        flash("Имя пользователя должно содержать от 6 до 20 символов.", "error")
                        return render_template("registration.html", theme=theme, form=form)
                    elif field == 'password':
                        if 'shorter than 6' in error:
                            flash("Пароль слишком короткий – минимум 6 символов.", "error")
                            return render_template("registration.html", theme=theme, form=form)
                        elif 'Invalid' in error:
                            flash("Пароль должен содержать хотя бы одну цифру и не иметь пробелов.", "error")
                            return render_template("registration.html", theme=theme, form=form)
                    elif field == 'password2':
                        flash("Пароли не совпадают.", "error")
                        return render_template("registration.html", theme=theme, form=form)

    return render_template("registration.html", theme=theme, form=form)


@app.route("/login", methods=['POST', 'GET'])
def login():
    theme = session.get("theme")
    form = LoginForm()
    if form.validate_on_submit():
        if form.register_btn.data:
            return redirect('/registration')
        else:
            db_sess = db_session.create_session()
            user = db_sess.query(User).filter(User.user == form.user.data).first()
            if user and user.check_password(form.password.data):
                login_user(user, remember=form.remember_me.data)
                return redirect('/')
            elif not user:
                flash('Такого пользователя не существует', 'error')
                return render_template("login.html", theme=theme, form=form)
            else:
                flash('Неверный пароль', 'error')
                return render_template("login.html", theme=theme, form=form)
    return render_template("login.html", theme=theme, form=form)

@app.route("/translate", methods=['POST', 'GET'])
def translate():
    theme = session.get("theme")
    if request.method == "POST":
        text = request.form["word"]
        result_check_word = check_word(text)
        if result_check_word[0]:
            translate = for_db.search_word(text)
            return render_template("translator.html", flag_translated=True, translated_text=translate, theme=theme, word=text)
        else:
            return render_template("translator.html", error_flag=True, error_code=result_check_word[-1], theme=theme)
    return render_template("translator.html", theme=theme)

@app.route("/toggle_theme", methods=["POST"])
def toggle_theme():
    current_theme = session.get("theme")
    if current_theme == "dark":
        session["theme"] = "light"
    elif current_theme == "light":
        session["theme"] = "dark"
    return redirect(request.referrer or url_for(hi_page))


@app.route('/add_to_dictionary', methods=["POST"])
@login_required
def add_to_dict():
    eng_word = request.form["word"]
    theme = session.get("theme")
    translation = request.form["translation"]
    flag_word = for_db.add_word_user_dict(current_user.user, eng_word)
    if flag_word:
        return render_template("translator.html", translated_text=translation, theme=theme, word=eng_word, word_added=True)
    else:
        return render_template("translator.html", translated_text=translation, theme=theme, word=eng_word, word_exists=True)

if __name__ == "__main__":
    #expire_at = Api.make_tokens.start_make_token()
    threading.Thread(target=monitor_token, daemon=True).start()
    db_session.global_init("db/Main.db")
    app.run(port=8080, host="127.0.0.1")
