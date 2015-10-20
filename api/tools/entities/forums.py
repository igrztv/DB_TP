

from api.tools import DBconnect
from api.tools.entities import users


def save_forum(name, short_name, user):
    DBconnect.exist(entity="user", identifier="email", value=user)
    forum = DBconnect.select_query(
        'select id, name, short_name, user FROM forum WHERE short_name = %s', (short_name, )
    )
    if len(forum) == 0:
        DBconnect.update_query('INSERT INTO forum (name, short_name, user) VALUES (%s, %s, %s)',
                               (name, short_name, user, ))
        forum = DBconnect.select_query(
            'select id, name, short_name, user FROM forum WHERE short_name = %s', (short_name, )
        )
    return forum_description(forum)


def forum_description(forum):
    forum = forum[0]
    response = {
        'id': forum[0],
        'name': forum[1],
        'short_name': forum[2],
        'user': forum[3]
    }
    return response


def details(short_name, related):
    forum = DBconnect.select_query(
        'select id, name, short_name, user FROM forum WHERE short_name = %s', (short_name, )
    )
    if len(forum) == 0:
        raise ("No forum with exists short_name=" + short_name)
    forum = forum_description(forum)

    if "user" in related:
        forum["user"] = users.details(forum["user"])
    return forum


def details_in(in_str):
    query = "SELECT id, name, short_name, user FROM forum WHERE short_name IN (%s);"
    forums = DBconnect.select_query(query, (in_str, ))
    forum_list = {}
    print(forums)
    for forum in forums:
        forum = {
            'id': forum[0],
            'name': forum[1],
            'short_name': forum[2],
            'user': forum[3]
        }
        forum_list[forum['short_name']] = forum
    return forum_list


def list_users(short_name, optional):
    # DBconnect.exist(entity="forum", identifier="short_name", value=short_name)
    query = "SELECT user.id, user.email, user.name, user.username, user.isAnonymous, user.about FROM user USE KEY (name_email) " \
        "WHERE user.email IN (SELECT DISTINCT user FROM post USE KEY (forum_user) WHERE forum = %s)"

    if "since_id" in optional:
        query += " AND user.id >= " + str(optional["since_id"])
    if "order" in optional:
        query += " ORDER BY user.name " + optional["order"]
    # else:
        # query += " ORDER BY user.name DESC"
    if "limit" in optional:
        query += " LIMIT " + str(optional["limit"])
    users_tuple = DBconnect.select_query(query, (short_name, ))
    list_u = []

    for user_sql in users_tuple:
        email = user_sql[1]
        list_u.append({
            'id': user_sql[0],
            'email': email,
            'name': user_sql[2],
            'username': user_sql[3],
            'isAnonymous': user_sql[4],
            'about': user_sql[5],
            'subscriptions': users.user_subscriptions(email),
            'followers': users.followers(email, "follower"),
            'following': users.followers(email, "followee")
        })

    return list_u
