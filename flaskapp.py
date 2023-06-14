from flask import Flask, render_template, url_for, request, redirect, send_from_directory, make_response
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import jwt
import bcrypt
import urllib
import os
from bson.objectid import ObjectId
from decouple import config
from datetime import datetime


DB_URL = "mongodb+srv://Sriram:SAEEnk6IZumLzqlN@cluster0.2y0zauv.mongodb.net/vaccineDetails"
SECRET_KEY = config('SECRET_KEY')

app = Flask(__name__)
app.secret_key = SECRET_KEY

# -------------------------------DATABASE---------------------------------

app.config["MONGO_URI"] = DB_URL
mongodb_client = PyMongo(app)
db = mongodb_client.db

# --------------------------JWT SESSION MANAGMENT--------------------------


def encodeJWT(userName):
    userData = db.users.find_one({'username':userName});
    encoded_token = jwt.encode(
        {'uname': userName, 'isAdmin': userData['isAdmin']}, SECRET_KEY, algorithm='HS256')
    return encoded_token


def decodeJWT(jwtToken):
    try:
        decoded_Payload = jwt.decode(
            jwtToken, SECRET_KEY, algorithms=['HS256'])
        uName = decoded_Payload['uname']
        isAdmin = decoded_Payload['isAdmin']
        if uName != None:
            return [str(uName).strip(), isAdmin]
        else:
            return None
    except Exception as e:
        return None

# -----------------------------ROUTING FUNCTIONS-----------------------------


@app.route("/", methods=['GET', 'POST'])
def login():
    if request.cookies.get('auth'):
        return redirect('/home')

    if request.method == 'POST':
        try:
            username = str(request.form['username']).strip()
            login_user = db.users.find_one(
                {'username': username})
            if login_user:
                if check_password_hash(login_user['password'], request.form['password']):
                    response = make_response(redirect('/home'))
                    response.set_cookie('auth', encodeJWT(
                        username), httponly=False)
                    return response

            return render_template('login.html', data="Invalid Credentials")

        except Exception as e:
            print(e)
            return redirect('/')
    
    return render_template('login.html', data='')

@app.route("/admin")
def admin():
    auth_cookie = request.cookies.get('auth')
    try:
        userName, checkAdmin = decodeJWT(auth_cookie)
        if checkAdmin==True:
            data = list(db.location.find({}))
            return render_template('admin.html', data=data)
        else:
            response = make_response(redirect('/'))
            response.delete_cookie('auth')
            return response

    except Exception as e:
        print(e)
        return redirect('/')


@app.route("/home")
def index():
    auth_cookie = request.cookies.get('auth')
    try:
        userName, checkAdmin = decodeJWT(auth_cookie)
        if userName:
            return render_template('index.html', data='')
        else:
            response = make_response(redirect('/'))
            response.delete_cookie('auth')
            return response

    except Exception as e:
        print(e)
        return redirect('/')


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            username = str(request.form['username']).strip()
            existing_user = db.users.find_one(
                {'username': username})

            if existing_user is None:
                if username == 'defaultProfile':
                    return render_template('login.html', data="Choose a different username.")

                hashpass = generate_password_hash(
                    str(request.form['password']), "sha256")
                address = str(request.form['address'])
                gender = str(request.form['gender'])
                age = str(request.form['age'])
                db.users.insert_one(
                    {
                        'username': username,
                        'password': hashpass,
                        'address': address,
                        'gender': gender,
                        'age': age,
                        'center': "",
                        'isAdmin': False
                    })
                response = make_response(redirect('/home'))
                response.set_cookie('auth', encodeJWT(
                    username), httponly=False)
                return response
            else:
                return render_template('login.html', data="Username already exist.")
        except Exception as e:
            print(e)
            return redirect('/')

    return render_template('register.html')


@app.route("/profile", methods=['GET', 'POST'])
def profile():
    auth_cookie = request.cookies.get('auth')
    try:
        if decodeJWT(auth_cookie):
            userName, checkAdmin = decodeJWT(auth_cookie)
            data = db.users.find_one({'username': userName})
            return render_template('profile.html', data=data)

        else:
            return redirect('/')

    except Exception as e:
        print(e)
        return redirect('/')


@app.route("/search", methods=['GET', 'POST'])
def search():
    auth_cookie = request.cookies.get('auth')
    try:
        if decodeJWT(auth_cookie):
            if request.method == 'POST':
                searchedLocation= str(request.form['location']).lower()
                data = db.location.find_one({'location': searchedLocation})
                if data:
                    return render_template('location.html', data = data)

                return render_template('location.html', data = None)
            return redirect("/home")
        else:
            return redirect('/')

    except Exception as e:
        print(e)
        return redirect('/')

@app.route("/book", methods=['POST'])
def book():
    auth_cookie = request.cookies.get('auth')
    try:
        if decodeJWT(auth_cookie):
            if request.method == 'POST':
                userName, checkAdmin = decodeJWT(auth_cookie)
                searchedLocation= str(request.form['location']).lower()
                db.users.find_one_and_update({'username':userName}, {'$set':{"center": searchedLocation}})
                db.location.find_one_and_update({'location': searchedLocation}, {'$inc':{'seatRemaining':-1, 'dosageAvailable':-1}})
                return render_template("index.html", data="Successfully booked!!!")
            else:
                return render_template("index.html", data="Try Again!!!")
        else:
            return redirect('/')

    except Exception as e:
        print(e)
        return redirect('/')

@app.route("/add", methods=['POST'])
def add():
    auth_cookie = request.cookies.get('auth')
    try:
        if decodeJWT(auth_cookie):
            if request.method == 'POST':
                location = str(request.form['location']).lower()
                seats = str(request.form['seatRemaining']).lower()
                dosage = str(request.form['dosageAvailable']).lower()
                db.location.insert_one(
                    {
                        'location': location,
                        'isOpen': True,
                        'seatRemaining': seats,
                        'dosageAvailable': dosage
                    })
                return render_template("index.html", data="Successfully Added!!!")
            else:
                return render_template("index.html", data="Try Again!!!")
        else:
            return redirect('/')

    except Exception as e:
        print(e)
        return redirect('/')

@app.route("/delete", methods=['POST'])
def delete():
    auth_cookie = request.cookies.get('auth')
    try:
        if decodeJWT(auth_cookie):
            if request.method == 'POST':
                searchedLocation= str(request.form['location']).lower()
                data = db.location.delete_one({'location': searchedLocation})
                return render_template("index.html", data="Successfully Deleted!!!")
            else:
                return redirect("/")
        else:
            return redirect('/')

    except Exception as e:
        print(e)
        return redirect('/')

@app.route("/logout")
def logout():
    response = make_response(redirect('/'))
    response.delete_cookie('auth')
    return response


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
