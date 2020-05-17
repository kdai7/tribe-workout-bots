from winter_db import *
from wreck_winter_challenge import WreckAWinter
from slack_api import *
from time import sleep
import json

from flask import Flask, request, jsonify, make_response

app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    print("event received")
    GYM_POINTS = 1.0
    THROW_POINTS = 1.0
    CARDIO_POINTS = 0.5
    CHALLENGE_POINTS = 1.5
    BOT_CHANNEL = "CBJAJPZ8B"
    data = request.get_json()
    if data['type'] == "url_verification":
        return jsonify({'challenge': data['challenge']})
    print('HTTP_X_SLACK_RETRY_NUM' in list(request.__dict__['environ'].keys()))
    if 'HTTP_X_SLACK_RETRY_NUM' in list(request.__dict__['environ'].keys()):
        print("Retry Number " + request.__dict__['environ']['HTTP_X_SLACK_RETRY_NUM'])
        if int(request.__dict__['environ']['HTTP_X_SLACK_RETRY_NUM']):
            return make_response("Ok", 200, )
    print(data)
    obj = WreckAWinter(data)
    if not obj._bot and not obj._reaction_added and not obj._reaction_removed:
        print("not a bot")
        obj.isRepeat()
        obj._repeat = False
        if obj._points_to_add > 0:
            print("points to add")
            obj.handle_db()
        else:
            print("executing commands")
            obj.execute_commands()

    print(obj)
    print("responding")
    return make_response("Ok", 200, )
