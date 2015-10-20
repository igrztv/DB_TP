

from api.tools import DBconnect


def status():
    statuses = DBconnect.select_query('''SELECT table_name, table_rows
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'forumdb'
AND table_name IN ('user', 'thread', 'forum', 'post')''', [])
    result = {}
    for status in statuses:
        result[status[0]] = status[1]
    return result
