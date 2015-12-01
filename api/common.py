def list_following(cursor, user_id):
    cursor.execute("""SELECT followee FROM follower WHERE follower = %s;""", (user_id, ))
    following = [i['followee'] for i in cursor.fetchall()]

    return following


def list_followers(cursor, user_id):
    cursor.execute("""SELECT follower FROM follower WHERE followee = %s;""", (user_id, ))
    followers = [i['follower'] for i in cursor.fetchall()]

    return followers


def user_details(cursor, email):
    cursor.execute("""SELECT * FROM `user` WHERE `email` = %s LIMIT 1;""", (email, ))
    user = cursor.fetchone()

    if user is None:
        return None

    following = list_following(cursor, email)
    followers = list_followers(cursor, email)

    cursor.execute("""SELECT `thread` FROM `subscription` WHERE `user` = %s;""", (email, ))
    threads = [i['thread'] for i in cursor.fetchall()]

    user.update({'following': following, 'followers': followers, 'subscriptions': threads})
    return user


def forum_details(cursor, short_name):
    cursor.execute("""SELECT * FROM `forum` WHERE `short_name` = %s LIMIT 1;""", (short_name, ))
    forum = cursor.fetchone()
    return forum


def thread_details(cursor, id):
    cursor.execute("""SELECT * FROM `thread` WHERE `id` = %s;""", (id, ))
    thread = cursor.fetchone()

    if thread is None:
        return None

    thread.update({'date': str(thread['date'])})  # TODO: bad code
    return thread


def post_details(cursor, id):
    cursor.execute("""SELECT * FROM `posts` WHERE `id` = %s;""", id)
    post = cursor.fetchone()

    if post is None:
        return None

    post.update({'date': str(post['date'])})  # TODO: bad code
    return post