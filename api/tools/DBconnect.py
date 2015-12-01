

import MySQLdb as db


class DBConnection:

    def __init__(self):
        pass

    # Main connector method
    @staticmethod
    def connect():
        return db.connect(host="127.0.0.1", user="root", passwd="Qwerty123!", db="forumdb")


# Execute update query
def update_query(query, params):
    try:
        con = DBConnection()
        con = con.connect()
        cursor = con.cursor()
        cursor.execute(query, params)
        con.commit()
        inserted_id = cursor.lastrowid

        cursor.close()
        con.close()
    except db.Error:
        raise db.Error("Database error in update query.")
    return inserted_id


# Execute query
# Returns tuple!
def select_query(query, params):
    try:
        con = DBConnection()
        con = con.connect()
        cursor = con.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        con.close()
    except db.Error:
        raise db.Error("Database error in usual query")
    return result


# Check if something exists
def exist(entity, identifier, value):
    if not len(select_query('SELECT id FROM ' + entity + ' WHERE ' + identifier + '=%s', (value, ))):
        raise Exception("No such element in " + entity + " with " + identifier + "=" + str(value))
    return


def execute(query):
    # try:
    con = DBConnection()
    con = con.connect()
    cursor = con.cursor()
    cursor.execute(query)
    con.commit()
    cursor.close()
    con.close()
    # except db.Error:
    #     raise db.Error("Database error in update query.")
    return
