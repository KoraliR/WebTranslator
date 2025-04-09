from flask import Flask
from flask import render_template, request, flash, redirect, session, url_for

import Api.make_tokens
from db import for_db
from data import db_session
from string import ascii_letters
from string import punctuation

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


@app.before_request
def set_default_theme():
    if "theme" not in session:
        session["theme"] = "light"


@app.route("/")
def hi_page():
    theme = session.get("theme")
    return render_template("start.html", theme=theme)

@app.route("/login")
def login_page():
    return render_template("login.html")

@app.route("/registraion")
def registration_page():
    return render_template("registration.html")

@app.route("/account")
def account():
    return render_template("account.html")

@app.route("/translate", methods=['POST', 'GET'])
def translate():
    theme = session.get("theme")
    if request.method == "POST":
        text = request.form["word"]
        result_check_word = check_word(text)
        if result_check_word[0]:
            translate = for_db.search_word(text)
            return render_template("translator.html", flag_registration=True, flag_translated=True, translated_text=translate, theme=theme)
        else:
            return render_template("translator.html", flag_registration=True, error_flag=True, error_code=result_check_word[-1], theme=theme)
    return render_template("translator.html", flag_registration=True, theme=theme)
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
