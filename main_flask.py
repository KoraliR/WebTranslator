from flask import Flask
from flask import render_template, request, flash, redirect, session, url_for

import Api.make_tokens
from db import for_db
from data import db_session, users
from string import ascii_letters
from string import punctuation
import re


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
    flag_registration = False
    login = ''


@app.route("/")
def hi_page():
    global flag_registration, login
    theme = session.get("theme")
    return render_template("start.html", flag_registration=flag_registration, theme=theme, login=login)

@app.route("/account")
def login_page():
    return render_template("account.html")

@app.route("/registration", methods=['POST', 'GET'])
def registration_page():
    global flag_registration, login
    theme = session.get("theme")
    if request.method == "POST":
        login = request.form["login"]
        password = request.form['password']
        password1 = request.form['password1']
        result_check_login_and_password_r = check_login_and_password_reg(login, password, password1)
        if result_check_login_and_password_r[0]:
            for_db.append_user(login, password)
            flag_registration = True 
            return render_template("start.html", flag_registration=flag_registration, login=login, theme=theme)
        else:
            return render_template("registration.html", error_flag=True, error_code=result_check_login_and_password_r[-1], theme=theme, login=login)
    return render_template("registration.html", theme=theme, login=login)

@app.route("/log_in", methods=['POST', 'GET'])
def log_in():
    global flag_registration, login
    theme = session.get("theme")
    if request.method == "POST":
        login = request.form["login"]
        password = request.form['password']
        result_check_login_and_password = check_login_and_password_auth(login, password)
        if result_check_login_and_password[0]:
            flag_registration = True
            return render_template("start.html", flag_registration=flag_registration, login=login, theme=theme)
        else:
            return render_template("log_in.html", error_flag=True, error_code=result_check_login_and_password[-1], theme=theme, login=login)
    return render_template("log_in.html", theme=theme, login=login)

@app.route("/translate", methods=['POST', 'GET'])
def translate():
    global flag_registration, login
    theme = session.get("theme")
    if request.method == "POST":
        text = request.form["word"]
        result_check_word = check_word(text)
        if result_check_word[0]:
            translate = for_db.search_word(text)
            return render_template("translator.html", flag_registration=True, flag_translated=True, translated_text=translate, theme=theme, login=login)
        else:
            return render_template("translator.html", flag_registration=True, error_flag=True, login=login, error_code=result_check_word[-1], theme=theme)
    return render_template("translator.html", flag_registration=True, login=login, theme=theme)
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
    return redirect(request.referrer or url_for("/"))







if __name__ == "__main__":
    #expire_at = Api.make_tokens.start_make_token()
    db_session.global_init("db/Main.db")
    app.run(port=8080, host="127.0.0.1")
