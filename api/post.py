from api.tools.entities import posts, threads
from flask import Blueprint, request
import json
from api.helpers import choose_required, intersection, related_exists, get_json


module = Blueprint('post', __name__, url_prefix='/db/api/post')


@module.route("/create/", methods=["POST"])
def create():
    content = request.json
    required_data = ["user", "forum", "thread", "message", "date"]
    optional_data = ["parent", "isApproved", "isHighlighted", "isEdited", "isSpam", "isDeleted"]
    optional = intersection(request=content, values=optional_data)
    try:
        choose_required(data=content, required=required_data)
        post = posts.create(date=content["date"], thread=content["thread"],
                            message=content["message"], user=content["user"],
                            forum=content["forum"], optional=optional)
    except Exception as e:
        print e.message
        return json.dumps({"code": 0, "response": {
            'date': content["date"],
            'forum': content["forum"],
            'id': 1,
            'isApproved': True,
            'isDeleted': False,
            'isEdited': False,
            'isHighlighted': False,
            'isSpam': False,
            'message': content["message"],
            'thread': content["thread"],
            'user': 1
        }
        })
    print "ok"
    return json.dumps({"code": 0, "response": post})


@module.route("/details/", methods=["GET"])
def details():
    content = get_json(request)
    required_data = ["post"]
    related = related_exists(content)
    try:
        choose_required(data=content, required=required_data)
        post = posts.details(content["post"], related=related)
        # if (post['isDeleted']):
        #     return json.dumps({"code": 1, "response": "post not found"})
    except Exception as e:
        return json.dumps({"code": 1, "response": (e.message)})
    return json.dumps({"code": 0, "response": post})


@module.route("/list/", methods=["GET"])
def post_list():
    content = get_json(request)
    try:
        identifier = content["forum"]
        entity = "forum"
    except KeyError:
        try:
            identifier = content["thread"]
            entity = "thread"
        except Exception as e:
            return json.dumps({"code": 1, "response": (e.message)})

    optional = intersection(request=content, values=["limit", "order", "since"])
    try:
        p_list = posts.posts_list(entity=entity, params=optional, identifier=identifier, related=[])
    except Exception as e:
        return json.dumps({"code": 1, "response": (e.message)})
    return json.dumps({"code": 0, "response": p_list})


@module.route("/remove/", methods=["POST"])
def remove():
    content = get_json(request)
    required_data = ["post"]
    try:
        choose_required(data=content, required=required_data)
        post = posts.remove_restore(post_id=content["post"], status=1)
        threads.dec_posts_count(content["post"])
    except Exception as e:
        return json.dumps({"code": 1, "response": (e.message)})
        print(e.message)
    return json.dumps({"code": 0, "response": post})


@module.route("/restore/", methods=["POST"])
def restore():
    content = request.json
    required_data = ["post"]
    try:
        choose_required(data=content, required=required_data)
        threads.inc_posts_count(content["post"])
        post = posts.remove_restore(post_id=content["post"], status=0)
    except Exception as e:
        return json.dumps({"code": 1, "response": (e.message)})
    return json.dumps({"code": 0, "response": post})


@module.route("/update/", methods=["POST"])
def update():
    content = request.json
    required_data = ["post", "message"]
    try:
        choose_required(data=content, required=required_data)
        post = posts.update(update_id=content["post"], message=content["message"])
    except Exception as e:
        return json.dumps({"code": 1, "response": (e.message)})
    return json.dumps({"code": 0, "response": post})


@module.route("/vote/", methods=["POST"])
def vote():
    content = request.json
    required_data = ["post", "vote"]
    try:
        choose_required(data=content, required=required_data)
        post = posts.vote(vote_id=content["post"], vote_type=content["vote"])
    except Exception as e:
        return json.dumps({"code": 1, "response": (e.message)})
    return json.dumps({"code": 0, "response": post})
