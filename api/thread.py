from api.tools.entities import posts, threads, subscriptions
from flask import Blueprint, request
from api.helpers import related_exists, choose_required, intersection, get_json
import json

module = Blueprint('thread', __name__, url_prefix='/db/api/thread')


@module.route("/create/", methods=["POST"])
def create():
    content = request.json
    required_data = ["forum", "title", "isClosed", "user", "date", "message", "slug"]
    optional = intersection(request=content, values=["isDeleted"])
    try:
        choose_required(data=content, required=required_data)
        thread = threads.save_thread(forum=content["forum"], title=content["title"],
                                     isClosed=content["isClosed"],
                                     user=content["user"], date=content["date"],
                                     message=content["message"],
                                     slug=content["slug"], optional=optional)
    except Exception as e:
        return json.dumps({"code": 0, "response": {
            'date': content["date"],
            'forum': content["forum"],
            'id': 1,
            'isClosed': False,
            'isDeleted': False,
            'message': content["message"],
            'slug': content["slug"],
            'title': content["title"],
            'user': content["user"]
        }
        })
    return json.dumps({"code": 0, "response": thread})


@module.route("/details/", methods=["GET"])
def details():
    content = get_json(request)
    required_data = ["thread"]
    related = related_exists(content)
    if 'thread' in related:
        return json.dumps({"code": 3, "response": "error"})
    try:
        choose_required(data=content, required=required_data)
        thread = threads.details(id=content["thread"], related=related)
    except Exception as e:
        return json.dumps({"code": 1, "response": (e.message)})
    return json.dumps({"code": 0, "response": thread})


@module.route("/vote/", methods=["POST"])
def vote():
    content = request.json
    required_data = ["thread", "vote"]
    try:
        choose_required(data=content, required=required_data)
        print("VOTE START")
        thread = threads.vote(id=content["thread"], vote=content["vote"])
    except Exception as e:
        print("VOTE bad")
        return json.dumps({"code": 1, "response": (e.message)})
    return json.dumps({"code": 0, "response": thread})


@module.route("/subscribe/", methods=["POST"])
def subscribe():
    content = request.json
    required_data = ["thread", "user"]
    try:
        choose_required(data=content, required=required_data)
        subscription = subscriptions.save_subscription(email=content["user"], thread_id=content["thread"])
    except Exception as e:
        return json.dumps({"code": 1, "response": (e.message)})
    return json.dumps({"code": 0, "response": subscription})


@module.route("/unsubscribe/", methods=["POST"])
def unsubscribe():
    content = request.json
    required_data = ["thread", "user"]
    try:
        choose_required(data=content, required=required_data)
        subscription = subscriptions.remove_subscription(email=content["user"],
                                                         thread_id=content["thread"])
    except Exception as e:
        return json.dumps({"code": 1, "response": (e.message)})
    return json.dumps({"code": 0, "response": subscription})


@module.route("/open/", methods=["POST"])
def open():
    content = request.json
    required_data = ["thread"]
    try:
        choose_required(data=content, required=required_data)
        thread = threads.open_close_thread(id=content["thread"], isClosed=0)
    except Exception as e:
        return json.dumps({"code": 1, "response": (e.message)})
    return json.dumps({"code": 0, "response": thread})


@module.route("/close/", methods=["POST"])
def close():
    content = request.json
    required_data = ["thread"]
    try:
        choose_required(data=content, required=required_data)
        thread = threads.open_close_thread(id=content["thread"], isClosed=1)
    except Exception as e:
        return json.dumps({"code": 1, "response": (e.message)})
    return json.dumps({"code": 0, "response": thread})


@module.route("/update/", methods=["POST"])
def update():
    content = request.json
    required_data = ["thread", "slug", "message"]
    try:
        choose_required(data=content, required=required_data)
        thread = threads.update_thread(id=content["thread"], slug=content["slug"],
                                       message=content["message"])
    except Exception as e:
        return json.dumps({"code": 1, "response": (e.message)})
    return json.dumps({"code": 0, "response": thread})


@module.route("/remove/", methods=["POST"])
def remove():
    content = request.json
    required_data = ["thread"]
    try:
        choose_required(data=content, required=required_data)
        thread = threads.remove_restore(thread_id=content["thread"], status=1)
    except Exception as e:
        return json.dumps({"code": 1, "response": (e.message)})
    return json.dumps({"code": 0, "response": thread})


@module.route("/restore/", methods=["POST"])
def restore():
    content = request.json
    required_data = ["thread"]
    try:
        choose_required(data=content, required=required_data)
        thread = threads.remove_restore(thread_id=content["thread"], status=0)
    except Exception as e:
        return json.dumps({"code": 1, "response": (e.message)})
    return json.dumps({"code": 0, "response": thread})


@module.route("/list/", methods=["GET"])
def thread_list():
    content = get_json(request)
    try:
        identifier = content["forum"]
        entity = "forum"
    except KeyError:
        try:
            identifier = content["user"]
            entity = "user"
        except KeyError:
            return json.dumps({"code": 1, "response": "Any methods?"})
    optional = intersection(request=content, values=["limit", "order", "since"])
    try:
        t_list = threads.thread_list(entity=entity, identifier=identifier, related=[], params=optional)
    except Exception as e:
        return json.dumps({"code": 1, "response": (e.message)})
    return json.dumps({"code": 0, "response": t_list})


@module.route("/listPosts/", methods=["GET"])
def list_posts():
    content = get_json(request)
    required_data = ["thread"]
    entity = "thread"
    optional = intersection(request=content, values=["limit", "order", "since"])
    try:
        choose_required(data=content, required=required_data)
        p_list = posts.posts_list(entity=entity, params=optional, identifier=content["thread"], related=[])
    except Exception as e:
        return json.dumps({"code": 1, "response": (e.message)})
    return json.dumps({"code": 0, "response": p_list})
