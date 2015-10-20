from api.tools.entities import users, forums, threads
from api.tools import DBconnect
from api.tools.DBconnect import DBConnection
import time

def create(date, thread, message, user, forum, optional):
    DBconnect.exist(entity="thread", identifier="id", value=thread)
    DBconnect.exist(entity="forum", identifier="short_name", value=forum)
    DBconnect.exist(entity="user", identifier="email", value=user)
    print (date, thread, message, user, forum, optional)
    if len(DBconnect.select_query("SELECT thread.id as id FROM thread JOIN forum ON thread.forum = forum.short_name "
                                "WHERE thread.forum = %s AND thread.id = %s", (forum, thread, ))) == 0:
        raise Exception("no thread with id = " + str(thread) + " in forum " + forum)
    if (("parent" in optional) and (optional["parent"] != None)):
        if len(DBconnect.select_query("SELECT post.id FROM post JOIN thread ON thread.id = post.thread "
                                    "WHERE post.id = %s AND thread.id = %s", (optional["parent"], thread, ))) == 0:
            raise Exception("No post with id = " + optional["parent"])
    try:
        query = "INSERT INTO post (message, user, forum, thread, date"
        values = "(%s, %s, %s, %s, %s"
        parameters = [message, user, forum, thread, date]

        #optional_data = ["parent", "isApproved", "isHighlighted", "isEdited", "isSpam", "isDeleted"]
        for param in optional:
            query += ", " + param
            values += ", %s"
            parameters.append(optional[param])
    except Exception as e:
        print e.message
    query += ") VALUES " + values + ")"

    update_thread_posts = "UPDATE thread SET posts = posts + 1 WHERE id = %s"
    con = DBConnection()
    con = con.connect()
    con.autocommit(False)
    with con:
        cursor = con.cursor()
        try:
            con.begin()
            cursor.execute(update_thread_posts, (thread, ))
            cursor.execute(query, parameters)
            con.commit()
        except Exception as e:
            con.rollback()
            raise Exception("Database error: " + e.message)
        post_id = cursor.lastrowid
        cursor.close()

    con.close()
    post = post_query(post_id)
    del post["dislikes"]
    del post["likes"]
    del post["parent"]
    del post["points"]
    return post


def details(details_id, related):
    post = post_query(details_id)
    if post is None:
        raise Exception("no post with id = " + details_id)

    if "user" in related:
        post["user"] = users.details(post["user"])
    if "forum" in related:
        post["forum"] = forums.details(short_name=post["forum"], related=[])
    if "thread" in related:
        post["thread"] = threads.details(id=post["thread"], related=[])

    return post


def posts_list(entity, params, identifier, related=[]):
    # if entity == "forum":
    #     DBconnect.exist(entity="forum", identifier="short_name", value=identifier)
    # if entity == "thread":
    #     DBconnect.exist(entity="thread", identifier="id", value=identifier)
    # if entity == "user":
    #     DBconnect.exist(entity="user", identifier="email", value=identifier)
    # query = "SELECT date, dislikes, forum, id, isApproved, isDeleted, isEdited, isHighlighted, isSpam, likes, message,
    #  parent, points, thread, user FROM post WHERE " + entity + " = %s "

    query = "SELECT date, dislikes, forum, id, isApproved, isDeleted, isEdited, isHighlighted, isSpam, likes, message, " \
            "parent, points, thread, user FROM post WHERE " + entity + " = %s "

    parameters = [identifier]
    if "since" in params:
        query += " AND date >= %s"
        parameters.append(params["since"])
    if "order" in params:
        query += " ORDER BY date " + params["order"]
    else:
        query += " ORDER BY date DESC"
    if "limit" in params:
        query += " LIMIT " + str(params["limit"])

    print (query.format(identifier))
    begin = int(round(time.time() * 1000))
    post_ids = DBconnect.select_query(query=query, params=parameters)
    end = int(round(time.time() * 1000))
    print(end-begin)
    begin = int(round(time.time() * 1000))
    user_time = forum_time = thread_time = 0
    post_list = []
    related_user = ""
    related_forum = ""
    related_thread = ""
    for post in post_ids:
        if "user" in related:
            related_user += "'" + post[14] + "', "
        if "forum" in related:
            related_forum += "'" + post[2] + "', "
        if "thread" in related:
            related_thread += str(post[13]) + ", "

    if "user" in related:
        users_list = users.details_in(related_user[:len(related_user) - 2])
    if "forum" in related:
        forum_list = forums.details_in(related_forum[:len(related_forum) - 2])
    if "thread" in related:
        thread_list = threads.details_in(related_thread[:len(related_thread) - 2])

    for post in post_ids:
        pf = {
            'date': str(post[0]),
            'dislikes': post[1],
            'forum': post[2],
            'id': post[3],
            'isApproved': bool(post[4]),
            'isDeleted': bool(post[5]),
            'isEdited': bool(post[6]),
            'isHighlighted': bool(post[7]),
            'isSpam': bool(post[8]),
            'likes': post[9],
            'message': post[10],
            'parent': post[11],
            'points': post[12],
            'thread': post[13],
            'user': post[14],

        }
        if "user" in related:
            ubeg = int(round(time.time() * 1000))
            # pf["user"] = users.details(pf["user"])
            pf["user"] = users_list[pf["user"]]
            user_time += (int(round(time.time() * 1000)) - ubeg)
        if "forum" in related:
            fbeg = int(round(time.time() * 1000))
            # pf["forum"] = forums.details(short_name=pf["forum"], related=[])
            print("FORUM " + pf["forum"])
            print(forum_list)
            pf["forum"] = forum_list.get(pf["forum"])
            forum_time += (int(round(time.time() * 1000)) - fbeg)
        if "thread" in related:
            tbeg = int(round(time.time() * 1000))
            pf["thread"] = thread_list.get(int(pf["thread"]))
            thread_time += (int(round(time.time() * 1000)) - tbeg)
        post_list.append(pf)
    end = int(round(time.time() * 1000))
    print(end-begin)
    print("User %s" % (user_time, ))
    print("Forum %s" % (forum_time,))
    print("Thread %s" % (thread_time, ))
    return post_list


def remove_restore(post_id, status):
    DBconnect.exist(entity="post", identifier="id", value=post_id)
    DBconnect.update_query("UPDATE post SET isDeleted = %s WHERE post.id = %s", (status, post_id, ))
    return {
        "post": post_id
    }


def update(update_id, message):
    # DBconnect.exist(entity="post", identifier="id", value=update_id)
    DBconnect.update_query('UPDATE post SET message = %s WHERE id = %s', (message, update_id, ))
    return details(details_id=update_id, related=[])


def vote(vote_id, vote_type):
    # DBconnect.exist(entity="post", identifier="id", value=vote_id)
    if vote_type == -1:
        DBconnect.update_query("UPDATE post SET dislikes=dislikes+1, points=points-1 where id = %s", (vote_id, ))
    else:
        DBconnect.update_query("UPDATE post SET likes=likes+1, points=points+1  where id = %s", (vote_id, ))
    return details(details_id=vote_id, related=[])


def post_query(id):
    post = DBconnect.select_query('select date, dislikes, forum, id, isApproved, isDeleted, isEdited, '
                       'isHighlighted, isSpam, likes, message, parent, points, thread, user '
                       'FROM post WHERE id = %s', (id, ))
    if len(post) == 0:
        return None
    return post_formated(post)


def post_formated(post):
    post = post[0]
    post_response = {
        'date': str(post[0]),
        'dislikes': post[1],
        'forum': post[2],
        'id': post[3],
        'isApproved': bool(post[4]),
        'isDeleted': bool(post[5]),
        'isEdited': bool(post[6]),
        'isHighlighted': bool(post[7]),
        'isSpam': bool(post[8]),
        'likes': post[9],
        'message': post[10],
        'parent': post[11],
        'points': post[12],
        'thread': post[13],
        'user': post[14],

    }
    return post_response
