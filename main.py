import os
from flask import *
import psycopg2
from config import config
import re
import jwt
import time

app = Flask(__name__)

def isCorrect(s, pattern):
    return re.match(pattern, s) is not None


def isGoodPassword(password):
    if not(6 <= len(password)):
        return False
    haveDigit = False
    haveLowS = False
    haveUppS = False
    for elem in password:
        if elem.isdigit():
            haveDigit = True
        if elem.isalpha() and elem.islower():
            haveLowS = True
        if elem.isalpha() and elem.isupper():
            haveUppS = True
    if not(haveDigit and haveLowS and haveUppS):
        return False
    return True


def is_user_exists(login):
    # getting cursor
    params = config()
    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    # executing query
    query = f"SELECT * FROM customers WHERE (name='{login}')"
    cursor.execute(query)
    res = cursor.fetchall() # getting the result

    # closing cursor/connection
    cursor.close()
    connection.close()
    return (len(res) > 0)


def get_token_payload(token):
    if token == None:
        return "no token", False
    if "Bearer " not in token:
        return "no bearer", False
    token = token.replace("Bearer ", "")

    # is token valid?
    try:
        payload = jwt.decode(jwt=token, key="secret", algorithms=['HS256', 'RS256'])
    except:
        return "invalid token", False
    
    a = is_user_exists(payload.get("login", "sinny"))
    if not a:
        return "user does not exist", False

    # session ended
    if payload.get("death_time", 0) < time.time():
        return "session ended", False
    return payload, True


def register(login, email, password):
    if login == None or email == None or password == None:
        return "something missing", 400

    # verify content
    if not(isCorrect(login, "[a-zA-Z0-9-]+") and 1 <= len(login) <= 30):
        return "incorrect login", 400
    if not(1 <= len(email) <= 50):
        return "incorrect email", 400
    if not(isGoodPassword(password) and len(password) >= 6):
        return "bad password", 400

    # getting cursor
    params = config()
    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    # checking if user already exists
    query = f"SELECT name FROM customers WHERE (name='{login}' OR email='{email}')"
    cursor.execute(query)
    res = len(cursor.fetchall())
    if res > 0:
        cursor.close()
        connection.close()
        return "user already exists", 400

    # creating new user
    query = f"INSERT INTO customers(name, email, password) VALUES ('{login}', '{email}', '{password}')"
    cursor.execute(query)
    connection.commit() # updating table

    # closing cursor/connection
    cursor.close()
    connection.close()
    return "profile created", 201


@app.route('/api/ping', methods=['GET'])
def api_ping():
    return jsonify("ok"), 200


@app.route('/api/customers/', methods=["GET"])
def api_customers():
    # getting cursor
    params = config()
    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    # executing query
    query = "SELECT * FROM customers"
    cursor.execute(query)
    res = cursor.fetchall() # getting the result

    # closing cursor/connection
    cursor.close()
    connection.close()
    return res


@app.route('/sign-up', methods=["GET"])
def sign_up():
    return render_template("sign-up.html")

# create new user
@app.route('/api/sign-up', methods=["POST"])
def api_sign_up():
    data = request.get_json()
    login, email, password = data.get("login"), data.get("email"), data.get("password1")
    message, status = register(login, email, password)
    return jsonify(message), status


@app.route('/sign-in', methods=["GET"])
def sign_in():
    # if we have valid token, redirect to profile, else sign-in
    token = request.cookies.get("auth")
    if token != None:
        payload, bol = get_token_payload(token)
        if bol:
            return redirect('/profile')
    return render_template("sign-in.html")

# gives user his auth token
@app.route('/api/register', methods=["POST"])
def api_register():
    # user data
    data = request.get_json()
    login, password = data.get("login"), data.get("password")

    # creating cursor
    params = config()
    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    # checking if user already exists
    query = f"SELECT name FROM customers WHERE (name='{login}' AND password='{password}')"
    cursor.execute(query)
    res = len(cursor.fetchall())

    # closing cursor/connection
    cursor.close()
    connection.close()
    if res == 0:
        return jsonify({"reason": "wrong info"}), 400
    
    death_time = time.time() + 60
    token = "Bearer " + jwt.encode(payload={"login": login, "death_time": death_time}, key="secret", algorithm="HS256")
    return jsonify({"token": token}), 200


@app.route('/profile', methods=["GET"])
def profile():
    return render_template("profile.html")

# returns profile data using auth token
@app.route('/api/profile', methods=["GET"])
def api_profile():
    token = request.headers.get('Authorization')

    if token is None:
        token = request.cookies.get("auth")
    
    payload, bol = get_token_payload(token)
    if not bol:
        return jsonify(payload), 400
    login = payload.get("login")

    # creating cursor
    params = config()
    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    # finding this user
    query = f"SELECT name, email, password FROM customers WHERE (name='{login}')"
    cursor.execute(query)
    res = cursor.fetchall()

    # closing cursor/connection
    cursor.close()
    connection.close()

    res = res[0]
    return jsonify({"login": res[0], "email": res[1], "password": res[2]}), 200

# delete user account
@app.route('/api/delete-acc', methods=["DELETE"])
def api_delete():
    token = request.headers.get('Authorization')

    if token is None:
        token = request.cookies.get("auth")
    
    payload, bol = get_token_payload(token)
    if not bol:
        return jsonify(payload), 400
    login = payload.get("login")

    # creating cursor
    params = config()
    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    # deleting user
    query = f"DELETE FROM customers WHERE (name='{login}')"
    cursor.execute(query)
    connection.commit()

    # closing cursor/connection
    cursor.close()
    connection.close()
    
    return jsonify("user was successfully deleted"), 200

@app.route('/home', methods=["GET"])
def home():
    return render_template("home.html")

@app.route('/shop', methods=["GET"])
def shop():
    return render_template("shop.html")


if __name__ == '__main__':
    #port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=5000)

