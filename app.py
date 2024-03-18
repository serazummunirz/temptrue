from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

def db_connection():
    conn = None
    try:
        conn = sqlite3.connect('db.sqlite')
    except sqlite3.error as e:
        print(e)
    return conn



@app.route('/browsers', methods=['GET', 'POST'])
def browsers():
    conn = db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor = conn.execute("SELECT * FROM browser")
        browsers = [
            dict(id=row[0])
            for row in cursor.fetchall()
        ]
        if browsers is not None:
            return jsonify(browsers)
    
    elif request.method == 'POST':
        status = request.form['status']
        sql = """INSERT INTO browser (status)
                 VALUES (?, ?)"""
        cursor = cursor.execute(sql, (status))
        conn.commit()
        return f"Browser with the id: {cursor.lastrowid} created successfully"



@app.route('/browser/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def single_browser(id):
    # print(f"Request 1: {id}")
    conn = db_connection()
    cursor = conn.cursor()
    browser = None
    if request.method == 'GET':
        cursor.execute("SELECT * FROM browser WHERE id=?", (id,))
        rows = cursor.fetchall()
        for row in rows:
            browser = row
        if browser is not None:
            return jsonify(browser), 200
        else:
            return "Something wrong", 404

    elif request.method == 'PUT':
        # print(f"Reuqest PUT Initiated {id}")
        sql = """UPDATE browser
                SET status=?
                WHERE id=? """

        # print(f"Request: {request.json}")
        
        status = request.json['status']
 
        updated_browser = {
            "id": id,
            "status": status
        }
        # print(f"Update Browser: {updated_browser}")
        conn.execute(sql, (status, id))
        conn.commit()
        response = jsonify(updated_browser)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    elif request.method == 'DELETE':
        sql = """ DELETE FROM browser WHERE id=?"""
        conn.execute(sql, (id,))
        conn.commit()
        return f"The browser with id: {id} has been deleted", 200


@app.route('/id/<int:id>', methods=['GET', 'PUT'])
def browser_port(id):
    # print(f"ID: {id}")
    browser = None
    if request.method == 'GET':
        conn = db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM browser WHERE id=?", (id,))
        rows = cursor.fetchall()
        for row in rows:
            browser = row
        if browser is not None:
            return jsonify(browser), 200
        else:
            return "Something wrong", 404


    elif request.method == 'PUT':

        sql = """UPDATE browser
                SET status=? """
        
        status = 0

        updated_browser = {
            "status": status
        }

        # print(f"Update Browser: {updated_browser}")
        conn = db_connection()
        conn.execute(sql, (status,))
        conn.commit()

        response = jsonify(updated_browser)
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

if __name__ == '__main__':
    app.run()