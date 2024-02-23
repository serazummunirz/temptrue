import sqlite3, os

if os.path.exists('db.sqlite'):
    os.remove('db.sqlite')

conn = sqlite3.connect('db.sqlite')

cursor = conn.cursor()
sql_query = """ CREATE TABLE browser (
    id integer PRIMARY KEY,
    status integer NOT NULL
) """

try:
    cursor.execute(sql_query)
except sqlite3.OperationalError as e:
    print(e)

def setup_table():
    sql = """INSERT INTO browser (status) 
                VALUES (?)"""
    conn.execute(sql, (0,))
    conn.commit()

setup_table()