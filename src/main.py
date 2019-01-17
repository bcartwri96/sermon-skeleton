from flask import Flask
import controllers as cn

app = Flask(__name__)

@app.route("/")
def hello():
    return cn.index.main()
