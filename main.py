import os
from flask import *
import psycopg2
from config import config
import re
import jwt
import time

app = Flask(__name__)

def is_correct(s, pattern):
    return re.match(pattern, s) is not None


def is_good_password(password: str) -> bool:
    '''
    good password have:
    *more than 5 simbols
    *digits, lower case and upper case
    example: Aboba123
    '''
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


def sql_query(query, fetch=False, commit=False):
    # creating cursor
    params = config()
    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    # executing query
    cursor.execute(query)
    if fetch:
        res = cursor.fetchall() # getting the result
    if commit:
        connection.commit() # saving changes
    
    # closing cursor/connection
    cursor.close()
    connection.close()

    if fetch:
        return res

def does_user_exists(login: str) -> bool:
    '''
    checking if user with given login exists in database
    '''
    query = f"SELECT * FROM customers WHERE (login='{login}')"
    res = sql_query(query, fetch=True)

    return (len(res) > 0)


def get_token_payload(token: str) -> tuple:
    '''
    extracts payload with "death time" and user's login from token
    or if token invalid returns it's reason
    '''
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
    
    a = does_user_exists(payload.get("login", "sinny"))
    if not a:
        return "user does not exist", False

    # session ended
    if payload.get("death_time", 0) < time.time():
        return "session ended", False
    return payload, True


def register(login: str, email: str, password: str) -> tuple:
    '''
    adds profile with given params to database
    returns: (result, status)
    400: profile wasn't created
    201: profile created
    '''
    if login == None or email == None or password == None:
        return "something missing", 400

    # verify content
    if not(is_correct(login, "[a-zA-Z0-9-]+") and 1 <= len(login) <= 30):
        return "incorrect login", 400
    if not(1 <= len(email) <= 50):
        return "incorrect email", 400
    if not(is_good_password(password) and len(password) >= 6):
        return "bad password", 400

    # checking if profile already exists
    query = f"SELECT login FROM customers WHERE (login='{login}' OR email='{email}')"
    res = sql_query(query, fetch=True)
    if len(res) > 0:
        return "user already exists", 400

    # creating new profile
    query = f"INSERT INTO customers(login, email, password, basket) VALUES ('{login}', '{email}', '{password}', '')"
    sql_query(query, commit=True)

    return "profile created", 201


@app.route('/api/ping', methods=['GET'])
def api_ping():
    return jsonify("ok"), 200


@app.route('/api/customers/', methods=["GET"])
def api_customers():
    '''
    returns all user's info
    '''
    query = "SELECT * FROM customers"
    res = sql_query(query, fetch=True)

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

    # checking if user already exists
    query = f"SELECT login FROM customers WHERE (login='{login}' AND password='{password}')"
    res = sql_query(query, fetch=True)
    if len(res) == 0:
        return jsonify({"reason": "wrong info"}), 400
    
    death_time = time.time() + 60 * 60 * 24
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

    # finding this user
    query = f"SELECT login, email, password FROM customers WHERE (login='{login}')"
    res = sql_query(query, fetch=True)

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

    # deleting user
    query = f"DELETE FROM customers WHERE (login='{login}')"
    sql_query(query, commit=True)
    
    return jsonify("user was successfully deleted"), 200


# returns all products
@app.route('/api/products', methods=["GET"])
def api_products():
    order = request.args.get("order", "id")
    query = "SELECT * FROM products ORDER BY " + order
    res = sql_query(query, fetch=True)
    return jsonify(res), 200


@app.route('/home', methods=["GET"])
def home():
    return render_template("home.html")


@app.route('/shop', methods=["GET"])
def shop():
    return render_template("shop.html")


@app.route('/api/add-in-basket', methods=["GET"])
def api_add_basket():
    token = request.headers.get('Authorization')

    if token is None:
        token = request.cookies.get("auth")
    
    payload, bol = get_token_payload(token)
    if not bol:
        return jsonify({"res": payload}), 400
    login = payload.get("login")

    query = f"SELECT basket FROM customers WHERE (login='{login}')"
    res = sql_query(query, fetch=True)[0]
    M = res[0].split()
    product = request.args.get("product")
    if product in M:
        return jsonify({"res": "already in basket"}), 200
    M.append(product)
    basket = " ".join(M)
    
    query = f"UPDATE customers SET basket='{basket}' WHERE (login='{login}')"
    sql_query(query, commit=True)
    return jsonify({"res": "added in basket"}), 200


@app.route('/basket', methods=["GET"])
def basket():
    return render_template("basket.html")


if __name__ == '__main__':
    #port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=5000)

