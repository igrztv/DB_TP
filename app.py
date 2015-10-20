__author__ = 'dmitry'

from flask import Flask, request
from api.tools.entities.clear import clear as clear_db
import json
app = Flask(__name__)

app.config['DEBUG'] = True

from api.thread import module as thread
from api.user import module as user
from api.forum import module as forum
from api.post import module as post

app.register_blueprint(user)
app.register_blueprint(forum)
app.register_blueprint(thread)
app.register_blueprint(post)


@app.before_request
def before_request():
    print request
    print request.endpoint


@app.route('/db/api/clear/', methods=['POST'])
def clear():
    clear_db()
    return json.dumps({"code": 0, "response": "OK"})

if __name__ == '__main__':
    app.run(port=5000)
