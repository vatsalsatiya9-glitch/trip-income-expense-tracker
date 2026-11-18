import mysql.connector

print("Connecting to MySQL...")

database = mysql.connector.connect(
    host="127.0.0.1",
    port=3308,
    user="root",
    password="",
    database="tour_managenement.py",
    connection_timeout=5,
use_pure=True
)

print("MySQL Connected Successfully!")


def fetchData(sql, values=None):
    cursor = database.cursor(dictionary=True)
    cursor.execute(sql, values or ())
    result = cursor.fetchall()
    cursor.close()
    return result


def runSQL(sql, values=None):
    cursor = database.cursor()
    cursor.execute(sql, values or ())
    database.commit()
    result = cursor.rowcount
    cursor.close()
    return result



