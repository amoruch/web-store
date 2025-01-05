import os
from flask import *
import psycopg2
from config import config
import re
import jwt

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

def get_token_payload(token):
    if token == None:
        return "no token", False
    if "Bearer " not in token:
        return "no bearer", False
    token = token.replace("Bearer ", "")

    # Проверяем валидность токена
    try:
        payload = jwt.decode(jwt=token, key="secret", algorithms=['HS256', 'RS256'])
    except:
        return "invalid token", False
    return payload, True

def register(login, email, password):
    if login == None or email == None or password == None:
        return "go fuck yourself", 400

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


@app.route('/api/v1/customers/', methods=["GET"])
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
    return jsonify(res)


@app.route('/api/register', methods=["GET"])
def api_register():
    # user data
    data = request.get_json()
    login, password = data["login"], data["password"]

    # creating cursor
    params = config()
    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    # checking if user already exists
    query = f"SELECT name FROM customers WHERE (name='{login}' AND password='{password}')"
    cursor.execute(query)
    res = len(cursor.fetchall())
    if res == 0:
        return jsonify({"reason": "wrong info"}), 400

    token = jwt.encode(payload={"login": login}, key="secret", algorithm="HS256")
    return jsonify({"token": token}), 200


@app.route('/api/my-profile', methods=["GET"])
def api_profile():
    token = request.headers.get('Authorization')
    payload, bol = get_token_payload(token)
    if not bol:
        return jsonify(payload), 400
    login = payload["login"]

    # creating cursor
    params = config()
    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    # getting user info
    query = f"SELECT name, email, password FROM customers WHERE (name='{login}')"
    cursor.execute(query)
    res = cursor.fetchone()
    return jsonify(res), 200


@app.route('/sign-up', methods=["GET", "POST"])
def sign_up():
    message = ""

    if request.method == "POST":
        data = request.form
        login, email, password = data.get("login"), data.get("email"), data.get("password1")
        message, status = register(login, email, password)
        print(message, status)
    return render_template("sign-up.html", message=message)


@app.route('/profile', methods=["GET, POST"])
def profile():
    if request.method == "POST":
        data = request.form
        login, password = data.get("login"), data.get("password")
        
    token = request.headers.get('Authorization')

    if token is None:
        return render_template("sign-in.html")
    return render_template("profile.html")

if __name__ == '__main__':
    #port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=5000)

