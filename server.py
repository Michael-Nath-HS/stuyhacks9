from flask import Flask, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import ForeignKey
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy.orm import relationship
app = Flask(__name__)
import json
from pretty_bad_protocol import gnupg
import random, string

gpg = gnupg.GPG(binary="/usr/local/bin/gpg", options=["-n"])
config = json.loads(open("config.json").read())
app.secret_key = config["secret"]
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
db = SQLAlchemy(app)
def random_string():
    return ''.join([random.choice(string.ascii_lowercase + string.ascii_uppercase + string.digits) for i in range(16)])

@app.route('/api/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form["email"]
    user = db.session.query(User).filter_by(username=username).first()
    if user is not None:
        return ("username already exists", 400)
    # check if username exists in database
    password = request.form['password']
    # store in database 'users'; possibly implement email verification
    db.session.add(User(username,email,password))
    db.session.commit()
    return ("success", 200)

@app.route('/api/login', methods=['POST'])
def login():
    username = request.form['username']
    user = db.session.query(User).filter_by(username=username).first()
    if user is None:
        return ("user does not exist", 403)
    database_password = user.password_hash
    # database_password = whatever password we get from the database
    supplied_password = request.form['password']
    if check_password_hash(database_password, supplied_password):
        session['username'] = request.form['username']
        return ("success", 200)
    else:
        return ("wrong password", 403)

@app.route('/api/create_meetup', methods=['POST'])
def create_meetup():
    if "username" not in session:
        return ("unauthorized")
    meetup_info = {
        "id": random_string(),
        "owner": session["username"],
        "name": request.form["name"],
        "address": request.form["address"], # TODO: generate/validate with openstreetmap
        "description": request.form["description"],
        "key": request.form["key"],
        "private": True if request.form["private"] == "1" else False,
        "participants": str()
    }
    key_result = gpg.import_keys(meetup_info["key"])
    for result in key_result.results:
        if result["status"] == "Key expired" \
        or result["status"] == "No valid data found":
            return ("invalid key", 400)
    db.session.add(Event(meetup_info["id"], meetup_info["owner"], meetup_info["address"], meetup_info["description"], meetup_info["name"], meetup_info["private"], meetup_info["key"]))
    db.session.commit()
    return (meetup_info["id"], 200)

@app.route('/api/get_meetup/<meetup_id>', methods=['GET'])
def get_meetup(meetup_id):
    # meetup_info = stuff from DB
    meetup_info = db.session.query(Event).filter_by(event_id=meetup_id).first().__dict__
    if session["username"] != meetup_info["event_owner"]:
        del meetup_info["event_participants"]
    del meetup_info["event_key"]
    del meetup_info['_sa_instance_state']
    return meetup_info

@app.route('/api/invite_participant/<meetup_id>', methods=['GET'])
def invite_participant(meetup_id):
    # meetup_info = stuff from DB
    meetup_info = db.session.query(Event).filter_by(event_id=meetup_id).first().__dict__
    if session["username"] != meetup_info["event_owner"]:
        return ("you are not the owner", 403)
    invite_code = random_string()
    db.session.add(Participants(invite_code, None, None, meetup_id, None))
    # in db: name, email, event, response as 'unknown', invite code
    # the client will have to keep track of which invite code = which name and email
    # and verify itself
    db.session.commit()
    return invite_code

@app.route('/api/get_invitation/<meetup_id>/<invite_code>', methods=['GET'])
def get_invitation(meetup_id, invite_code):
    participant = db.session.query(Participants).filter_by(event_code=invite_code).first().__dict__
    meetup_info = db.session.query(Event).filter_by(event_id=meetup_id).first().__dict__
    print(meetup_info)
    if participant is None or participant["response"] is not None:
        return ("invite code invalid or already used", 400)
    # check if invite_code valid and not used, and if so

    # meetup_info = stuff from DB
    print(meetup_info)
    del meetup_info['_sa_instance_state']
    return meetup_info

@app.route('/api/respond_invitation/<meetup_id>/<invite_code>', methods=['POST'])
def respond_invitation(meetup_id, invite_code):
    response = int(request.form["response"]) # responses = ["Yes", "No", "Maybe"]
    name = request.form["name"]
    email = request.form["email"]
    meetup_info = db.session.query(Participants).filter_by(event_id=meetup_id).first()
    meetup_info.name = name
    meetup_info.email = email
    meetup_info.response = response
    # these should both be encrypted
    # put that in the database
    
    return ("success", 200)
    




class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    ownership = relationship("Event", backref="hosty")

    def __init__(self, username, email, password):
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
    event_key = db.Column(db.String, nullable=True)
    invitation_only = db.Column(db.Boolean, nullable=True)
    event_participants = []

    def __init__(self, event_id, host, event_address, event_description, event_name, invitation_only, event_key):
        self.event_id = event_id
        self.event_owner = host
        self.event_address = event_address
        self.event_description = event_description
        self.event_name = event_name
        self.invitation_only = invitation_only
        self.event_key = event_key

    def __repr__(self):
        return '<Event %r>' % self.event_name
    # participants = db.column(db.String(100), nullable=True)


class Participants(db.Model):
    __tablename__ = "table_participants"
    id = db.Column(db.Integer, primary_key=True)
    event_code = db.Column(db.String(16), nullable=True)
    name = db.Column(db.String, unique=True, nullable=True)
    # participant = relationship("Event", backref="participants", uselist=True)
    event_id = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=True)
    response = db.Column(db.Integer, nullable=True)

    def __init__(self, event_code, name, email, event_id, response):
        self.event_code = event_code
        self.name = name
        self.email = email
        self.event_id = event_id
        self.response = response

    def __repr__(self):
        return '<Participants %r>' % self.name
db.create_all()
app.run()