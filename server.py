from flask import Flask, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import ForeignKey
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.orm import relationship
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


db = SQLAlchemy(app)
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    ownership = relationship("Event", backref="owner")

    def __init__(self, id, username, email, password):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username


class Event(db.Model):
    __tablename__ = "events"
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String(16), unique=True, nullable=True)
    host = db.Column(db.String, ForeignKey("users.username"))
    event_address = db.Column(db.String(128), nullable=True)
    event_description = db.Column(db.String(250), nullable=True)
    event_name = db.Column(db.String(50), nullable=True)

    def __init__(self, id, event_id, host, event_address, event_description, event_name):
        self.id = id
        self.event_id = event_id
        self.host = host
        self.event_address = event_address
        self.event_description = event_description
        self.event_name = event_name

    def __repr__(self):
        return '<Event %r>' % self.event_name
    # participants = db.column(db.String(100), nullable=True)

