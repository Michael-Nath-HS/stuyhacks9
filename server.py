from flask import Flask, request, session, g
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
import json

config = json.loads(open("config.json").read())
app.secret_key = config["secret"]

@app.route('/api/signup', methods=['POST'])
def signup():
    username = request.form['username']
    # check if username exists in database
    password = generate_password_hash(request.form['password'])
    # store in database 'users'; possibly implement email verification
    return ("success", 200)

@app.route('/api/login', methods=['POST'])
def login():
    username = request.form['username']
    # database_password = whatever password we get from the database
    supplied_password = request.form['password']
    if check_password_hash(database_password, supplied_password):
        session['username'] = request.form['username']
        return ("success", 200)
    else:
        return ("wrong password", 403)


database = "pathtodatabase"
# con = sqlite3.connect("./db.sqlite3")
def db_connect(db_path=database):
    con = sqlite3.connect(db_path)
    return con

con = db_connect()



#
# def get_db():
#     db = getattr(g, "_database", None)
#     if db is None:
#         db = g._database = sqlite3.connect(database)
#     return db
#
# @app.teardown_appcontext
# def close_connection(exception):
#     db = getattr(g, '_database', None)
#     if db is not None:
#         db.close()
#
# @app.route("/")
# def index():
#     cur = get_db().cursor()
#
# def make_dicts(cursor, row):
#     return dict((cursor.description[idx][0], value)
#                 for idx, value in enumerate(row))
#
# db.row_factory = make_dicts