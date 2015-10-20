
from api.tools import DBconnect


def clear():
    tables = ['post', 'thread', 'forum', 'subscription', 'follower', 'user']
    DBconnect.execute("SET global foreign_key_checks = 0;")
    for table in tables:
        DBconnect.execute("TRUNCATE TABLE %s;" % table)
    DBconnect.execute("SET global foreign_key_checks = 1;")
    return