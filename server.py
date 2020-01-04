from flask import Flask, request, session
import random
imort string
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
import json

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
        "name": request.form["name"],
        "address": request.form["address"], # TODO: generate/validate with openstreetmap
        "description": request.form["description"],
        "key": request.form["key"], # TODO: validate with gnupg
        "participants": []
    }
    
