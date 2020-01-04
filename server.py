from flask import Flask, request, session
import random
imort string
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
import json
from pretty_bad_protocol import gnupg

gpg = gnupg.GPG(options=["-n"])
config = json.loads(open("config.json").read())
app.secret_key = config["secret"]

def random_string():
    return ''.join([random.choice(string.ascii_letters + string.ascii_uppercase + string.digits) for i in range(16)])

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
