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

def refreshProgress():
    status["finished"] = 0
    for h in status["helixes"].values():
        if h["finished"]:
            status["finished"] += 1
    status["progress"] = (100 * status["finished"]) / status["helix_count"]

def updateStatus():
    status["helix_count"] = len(status["helixes"])
    status["last_finish"] = status.get("last_finish", None)
    status["finish_order"] = status.get("finish_order", [])
    status["last_update"] = datetime.datetime.now().isoformat()
    refreshProgress()
    # all finished
    if status["progress"] == 100:
        status["last_finish"] = None

    # check if helix expired, but only if countdown is running
    if status["last_finish"]:
        lf = datetime.datetime.fromisoformat(status["last_finish"])
        if lf < datetime.datetime.now():
            unfinishHelix()
            refreshProgress()
    save_data(status)


def finishHelix(h):
    # skip if finished
    if str(h) in status["finish_order"]:
        return
    # mark helix as true and start countdown for it
    status["helixes"][str(h)]["finished"] = True
    status["finish_order"].append(str(h))
    helix = status["helixes"][str(h)]
    t = status["difficulties"][helix["difficulty"]]
    status["last_finish"] = (datetime.datetime.now() + datetime.timedelta(seconds=t)).isoformat()


def unfinishHelix():
    if(len(status["finish_order"])) > 1:
        # called when current helix times out
        # we pop that one out and unfinish it
        last = str(status["finish_order"].pop())
        status["helixes"][last]["finished"] = False

    if(len(status["finish_order"])) > 1:
        # then we pop another one and finish him
        # so the countdown for it can start again
        last = str(status["finish_order"].pop())
        finishHelix(last)
    else:
        status["last_finish"] = None
        return


status = load_data()

updateStatus()
save_data(status)


@app.route('/')
def hello_world():
    return 'OK'


@app.route("/status")
def get_status():
    print(status)
    # so we will kinda rely on periodical status check from FE and use it as hearbeat
    # without FE there is no need to have fresh data anyway, so it should be fine
    # except for helixes timeout if FE is dead for long time... YOLO

    updateStatus()
    return jsonify(status)


@app.route("/finish", methods=["POST"])
def finished_helix():
    h = request.form["helix"]
    finishHelix(h)
    return request.form
