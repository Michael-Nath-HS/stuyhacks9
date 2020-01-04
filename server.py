from flask import Flask, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import ForeignKey
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.orm import relationship
app = Flask(__name__)
import json
from pretty_bad_protocol import gnupg

gpg = gnupg.GPG(options=["-n"])
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

@app.route('/api/create_meetup', methods=['POST'])
def create_meetup():
    meetup_info = {
        "id": random_string(),
        "owner": session["username"],
        "name": request.form["name"],
        "address": request.form["address"], # TODO: generate/validate with openstreetmap
        "description": request.form["description"],
        "key": request.form["key"], 
        "participants": str()
    }
    key_result = gpg.import_keys(meetup_info["key"])
    for result in key_result.results:
        if result["status"] == "Key expired" \
        or result["status"] == "No valid data found":
            return ("invalid key", 400)

@app.route('/api/get_meetup/<meetup_id>', methods=['GET'])
def get_meetup(meetup_id):
    # meetup_info = stuff from DB
    if session["username"] != meetup_info["owner"]:
        del meetup_info["participants"]
    del meetup_info["key"]
    return meetup_info

@app.route('/api/invite_participant/<meetup_id>', methods=['GET'])
def invite_participant(meetup_id):
    # meetup_info = stuff from DB
    if session["username"] != meetup_info["owner"]:
        return ("you are not the owner", 403)
    invite_code = random_string()
    # in db: name, email, event, response as 'unknown', invite code
    # the client will have to keep track of which invite code = which name and email
    # and verify itself
    return invite_code

@app.route('/api/get_invitation/<meetup_id>/<invite_code>', methods=['GET'])
def get_invitation(meetup_id, invite_code):
    # check if invite_code valid and not used, and if so
        return ("invite code invalid or already used", 400)
    # meetup_info = stuff from DB
    del meetup_info["participants"]
    return meetup_info

@app.route('/api/respond_invitation/<meetup_id>/<invite_code>', methods=['POST'])
def respond_invitation(meetup_id, invite_code):
    response = int(request.form["response"]) # responses = ["Yes", "No", "Maybe"]
    name = request.form["name"]
    email = request.form["email"] # these should both be encrypted
    # put that in the database
    return ("success", 200)

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
    ownership = relationship("Event", backref="hosty")

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
    event_owner = db.Column(db.String, ForeignKey("users.username"))
    event_address = db.Column(db.String(128), nullable=True)
    event_description = db.Column(db.String(250), nullable=True)
    event_name = db.Column(db.String(50), nullable=True)
    invitation_only = db.Column(db.Boolean, nullable=True)
    event_participants = []

    def __init__(self, id, event_id, host, event_address, event_description, event_name, invitation_only):
        self.id = id
        self.event_id = event_id
        self.event_owner = host
        self.event_address = event_address
        self.event_description = event_description
        self.event_name = event_name
        self.invitation_only = invitation_only

    def __repr__(self):
        return '<Event %r>' % self.event_name
    # participants = db.column(db.String(100), nullable=True)


class Participants(db.Model):
    __tablename__ = "table_participants"
    id = db.Column(db.Integer, primary_key=True)
    event_code = db.Column(db.String(16), nullable=True)
    name = db.Column(db.String, unique=True, nullable=False)
    # participant = relationship("Event", backref="participants", uselist=True)
    event_id = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    response = db.Column(db.String, nullable=False)

    def __init__(self, id, event_code, name, email, event_id, response):
        self.id = id
        self.event_code = event_code
        self.name = name
        self.email = email
        self.event_id = event_id
        self.response = response

    def __repr__(self):
        return '<Participants %r>' % self.name