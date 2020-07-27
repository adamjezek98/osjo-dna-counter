from flask import Flask, jsonify, request
import datetime
import copy
import json

app = Flask(__name__)


def load_data():
    with open('data.json') as json_file:
        return json.load(json_file)


def save_data(data):
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)


def updateStatus():
    status["helix_count"] = len(status["helixes"])
    status["finished"] = 0
    status["last_finish"] = status.get("last_finish", None)
    status["finish_order"] = status.get("finish_order", [])
    for h in status["helixes"]:
        if h["completed"]:
            status["finished"] += 1
    status["progress"] = (100 * status["finished"]) / status["helix_count"]

    # all finished
    if status["progress"] == 100:
        status["last_finish"] = None

    # check if helix expired, but only if countdown is running
    if status["last_finish"]:
        lf = datetime.datetime.fromisoformat(status["last_finish"])
        if lf < datetime.datetime.now():
            unfinishHelix()
    save_data(status)


def finishHelix(h):
    # mark helix as true and start countdown for it
    status["helixes"][str(h)]["finished"] = True
    status["finish_order"].add(str(h))
    helix = status["helixes"][str(h)]
    t = status["difficulties"][helix["difficulty"]]
    status["last_finish"] = (datetime.datetime.now() + datetime.timedelta(minutes=t))


def unfinishHelix():
    # called when current helix times out
    # we pop that one out and unfinish it
    last = str(status["finish_order"].pop())
    status["helixes"][last]["finished"] = False

    # then we pop another one and finish him
    # so the countdown for it can start again
    last = str(status["finish_order"].pop())
    finished_helix(last)


status = load_data()

updateStatus()
save_data(status)


@app.route('/')
def hello_world():
    return 'OK'


@app.route("/status")
def get_status():
    print(status)
    print(type(status["helixes"][0]))
    return jsonify(status)


@app.route("/finish", methods=["POST"])
def finished_helix():
    h = request.form["helix"]
    finishHelix(h)
    return request.form
