from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from io import open as io_open
from urlparse import urlsplit
from PIL import Image

import requests
import datetime
import glob
import uuid
import os
import jwt


app = Flask(__name__)

file_path = os.path.abspath(os.getcwd())+"/todo.db"
image_url ="https://orig00.deviantart.net/5641/f/2016/159/9/7/deadpool_says_hiiii_by_poopy_artist-da5jdzi.jpg"
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] =  'sqlite:///'+file_path

db = SQLAlchemy(app)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    public_id = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(50))
    password = db.Column(db.String(80))
    admin = db.Column(db.Boolean)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        global token
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'mess' : 'Token missing!'}), 401
        try: 
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(public_id=data['public_id']).first()
        except:
            return jsonify({'mess' : 'Token invalid!'}), 401
        return f(current_user, *args, **kwargs)

    return decorated

@app.route('/user', methods=['GET'])
@token_required
def get_all_users(current_user):

    if not current_user.admin:
        return jsonify({'mes' : 'Function can not be performed'})

    getusers = User.query.all()
    out = []
    for user in getusers:
        user_info = {}
        user_info['public_id'] = user.public_id
        user_info['name'] = user.name
        user_info['password'] = user.password
        user_info['admin'] = user.admin
        out.append(user_info)

    return jsonify({'users' : out})

@app.route('/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(current_user, public_id):

    if not current_user.admin:
        return jsonify({'mess' : 'Cannot perform that function!'})

    user = User.query.filter_by(public_id=public_id).first()

    if not user:
        return jsonify({'mess' : 'No user found!'})

    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['admin'] = user.admin

    return jsonify({'user' : user_data})

@app.route('/createuser', methods=['POST'])
@token_required
def create_user(current_user): 
    if not current_user.admin:
        return jsonify({'mess' : 'Cannot perform that function!'})

    data = request.get_json()

    hashed_password = generate_password_hash(data['password'], method='sha256')

    new_user = User(public_id=str(uuid.uuid4()), name=data['name'], password=hashed_password, admin=False)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'mess' : 'New user created!'})


def download(file_url):
    suffix_list = ['jpg', 'gif', 'png', 'tif', 'svg',]
    file_name =  urlsplit(file_url)[2].split('/')[-1]
    file_suffix = file_name.split('.')[1]
    i = requests.get(file_url)
    if file_suffix in suffix_list and i.status_code == requests.codes.ok:
        with io_open(file_name, 'wb') as file:
            file.write(i.content)

@app.route('/thumb')
@token_required
def thumb(self):
	download(image_url)
	list = ["*.jpg","*png"]
	for l in list:
		for pic in glob.glob(l):
		  im = Image.open(pic)
		  im.thumbnail((50, 50))
		  if pic[0:2] != "Thumbnail_":
			im.save("Thumbnail_" + pic, "JPEG")
	return "thumbnail saved"

@app.route('/')
def login():
    global token
    auth = request.authorization

    if not auth or not auth.username or not auth.password:
        return make_response('Can not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    user = User.query.filter_by(name=auth.username).first()
    if not user:
        return make_response('Can not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

    if check_password_hash(user.password, auth.password):
        token_ = jwt.encode({'public_id' : user.public_id, 
			     'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)},
			      app.config['SECRET_KEY'])
	token = token_.decode('UTF-8')
	print token
        return jsonify({'token' : token_.decode('UTF-8')})

    return make_response('Could not verify', 401, {'WWW-Authenticate' : 'Basic realm="Login required!"'})

if __name__ == '__main__':
    app.run(debug=True)
