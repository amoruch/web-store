import os
from flask import *
import psycopg2
from config import config

app = Flask(__name__)

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

@app.route('/customer', methods=["POST"])
def add_customer():
    # getting cursor
    params = config()
    connection = psycopg2.connect(**params)
    cursor = connection.cursor()

    # creating new user
    query = "INSERT INTO customers(name, email) VALUES ('roman', 'aboba@e.huy')"
    cursor.execute(query)
    connection.commit() # updating table

    # closing cursor/connection
    cursor.close()
    connection.close()
    return jsonify({"status": 201})

@app.route('/sign-in')
def main_page():
    return render_template("sign-in.html")

if __name__ == '__main__':
    #port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=5000)

