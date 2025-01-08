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


def get_token_payload(token: str):
    """
    Returns token's payload or error reason in first varuable\n
    and status in second
    """
    if "Bearer " not in token:
        return {"reason": "no bearer"}, False
    token = token.replace("Bearer ", "")

    # Проверяем валидность токена
    try:
        payload = jwt.decode(jwt=token, key="secret", algorithms=['HS256', 'RS256'])
    except:
        return {"reason": "invalid token"}, False
    return payload, True


def register(login, email, password):
    """
    Using given login, email and password checking if they're valid\n
    if not, returns reason and status\n
    if they're valid, returns reason and status, and creates a new user account on server
    """
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


def del_user(login):
    pass


# sign-up for creating a new user account
@app.route('/sign-up', methods=["GET", "POST"])
def sign_up():
    message = ""

    if request.method == "POST":
        data = request.form
        login, email, password = data.get("login"), data.get("email"), data.get("password1")
        message, status = register(login, email, password)
    return make_response(render_template("sign-up.html", message=message))


@app.route('/api/register', methods=["GET"])
def api_register():
    # user data
    data = request.form
    login, password = data["login"], data["password"]

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
        return make_response(jsonify({"reason": "wrong info"}), 400)

    token = jwt.encode(payload={"login": login}, key="secret", algorithm="HS256")
    return make_response(jsonify({"token": token}), 200)


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

    # closing cursor/connection
    cursor.close()
    connection.close()
    return jsonify({"login": res[0], "email": res[1], "password": res[2]}), 200


@app.route('/profile', methods=["GET", "POST"])
def profile():
    if request.method == "POST": # if user sent us form with his info
        data = request.form
        if data.get("delete") is not None:
            token = request.cookies.get("auth")
            payload, bol = get_token_payload(token)
            login = payload.get("login")
            del_user(login)
        login, password = data.get("login"), data.get("password")
        
        # creating cursor
        params = config()
        connection = psycopg2.connect(**params)
        cursor = connection.cursor()

        # checking if user already exists
        query = f"SELECT name, email, password FROM customers WHERE (name='{login}' AND password='{password}')"
        cursor.execute(query)
        res = cursor.fetchall()

        # closing cursor/connection
        cursor.close()
        connection.close()

        if len(res) == 0: # if user not found
            return render_template("sign-in.html", message="incorrect login or password"), 200
        
        res = res[0]
        del_time = time.time() + 60 * 60 * 24
        token = jwt.encode(payload={"login": login, "del_time": del_time}, key="secret", algorithm="HS256")
        temp = render_template("profile.html", login=res[0], email=res[1], password=res[2])
        res = make_response(temp, 200)
        res.set_cookie("auth", "Bearer " + token)
        return res
        
    # looking for client's auth token
    token = request.headers.get('Authorization')
    if token is None:
        token = request.cookies.get("auth")
    
    # if token isn't found asking user to sign-in
    if token is None:
        return render_template("sign-in.html")
    
    # getting token payload
    payload, bol = get_token_payload(token)
    login = payload.get("login")
    del_time = payload.get("del_time")

    # if token time is invalid
    if del_time < time.time():
        temp = render_template("sign-in.html", message="your session ended")
        res = make_response(temp, 200)
        res.set_cookie("auth", "", max_age=0) # delete a token
        return res

    # creating cursor
    params = config()
    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    # checking if user already exists
    query = f"SELECT name, email, password FROM customers WHERE (name='{login}')"
    cursor.execute(query)
    res = cursor.fetchall()

    # closing cursor/connection
    cursor.close()
    connection.close()
    
    res = res[0]
    return render_template("profile.html", login=res[0], email=res[1], password=res[2])

@app.route('/home', methods=["GET"])
def home():
    return render_template("home.html")

@app.route('/shop', methods=["GET"])
def shop():
    return render_template("shop.html")

@app.route('/basket', methods=["GET"])
def basket():
    return render_template("basket.html")

if __name__ == '__main__':
    #port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=5000)

