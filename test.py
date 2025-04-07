from flask import Flask

app = Flask(__name__)

@app.route("/")
def main_f():
    return "Hi world!"



if __name__ == "__main__":
    app.run(port=8080, host="")
