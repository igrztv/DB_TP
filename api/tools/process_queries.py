__author__ = 'dmitry'

from api.tools import DBconnect
import MySQLdb as db


# Execute update query
def update_query(query, params):
    try:
        con = DBconnect.connect()
        cursor = con.cursor()
        cursor.execute(query, params)
        con.commit()
        inserted_id = cursor.lastrowid

        cursor.close()
        con.close()
    except db.Error as e:
        raise Exception(e.message)
    return inserted_id


# Execute query
# Returns tuple!
def select_query(query, params):
    try:
        con = DBconnect.connect()
        cursor = con.cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
        con.close()
    except db.Error as e:
        raise Exception(e.message)
    return result


# Check if something exists
def exist(entity, identifier, value):
    if not len(select_query('SELECT id FROM ' + entity + ' WHERE ' + identifier + '=%s', (value, ))):
        raise Exception("No such element in " + entity + " with " + identifier + "=" + str(value))
    return