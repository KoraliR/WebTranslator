from flask import Flask, render_template
from data.LoginForm import LoginForm

app = Flask(__name__)
app.secret_key = 'secret_key'

@app.route("/")
def main_f():
    form = LoginForm()
    return render_template('login.html', theme='light', form=form)

if __name__ == "__main__":
    app.run(port=8080, host="")
