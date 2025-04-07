from flask import Flask
from flask import render_template, request, flash, redirect
from db import for_db
from data import db_session

app = Flask(__name__)
app.secret_key = 'supersecretkey'

@app.route("/")
def hi_page():
    return render_template("start.html")

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
    if request.method == "POST":
        text = request.form["word"]
        translate = for_db.search_word(text)
        return f"Перевод {translate}"
    return render_template("translator.html")









if __name__ == "__main__":
    db_session.global_init("db/Main.db")
    app.run(port=8080, host="127.0.0.1")