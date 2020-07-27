from flask import Flask, jsonify, request, render_template
import datetime
import copy
import json

app = Flask(__name__)


def load_data():
    with open('data.json') as jsonFile:
        return json.load(jsonFile)


def save_data(data):
    with open('data.json', 'w') as outfile:
        json.dump(data, outfile)


def refreshProgress():
    status["finished"] = 0
    for h in status["helixes"].values():
        if h["finished"]:
            status["finished"] += 1
    status["progress"] = (100 * status["finished"]) / status["helixCount"]


def updateStatus():
    status["helixCount"] = len(status["helixes"])
    status["lastFinish"] = status.get("lastFinish", None)
    status["finishOrder"] = status.get("finishOrder", [])
    status["lastUpdate"] = datetime.datetime.now().isoformat()
    refreshProgress()
    # all finished
    if status["progress"] == 100:
        status["lastFinish"] = None

    # check if helix expired, but only if countdown is running
    if status["lastFinish"]:
        lf = datetime.datetime.fromisoformat(status["lastFinish"])
        if lf < datetime.datetime.now():
            unfinishHelix()
            refreshProgress()
    save_data(status)


def finishHelix(h):
    # skip if finished
    if str(h) in status["finishOrder"]:
        return
    # mark helix as true and start countdown for it
    status["helixes"][str(h)]["finished"] = True
    status["finishOrder"].append(str(h))
    helix = status["helixes"][str(h)]
    t = status["difficulties"][helix["difficulty"]]
    status["lastFinish"] = (datetime.datetime.now() + datetime.timedelta(seconds=t)).isoformat()


def unfinishHelix():
    if (len(status["finishOrder"])) > 1:
        # called when current helix times out
        # we pop that one out and unfinish it
        last = str(status["finishOrder"].pop())
        status["helixes"][last]["finished"] = False

    if (len(status["finishOrder"])) > 1:
        # then we pop another one and finish him
        # so the countdown for it can start again
        last = str(status["finishOrder"].pop())
        finishHelix(last)
    else:
        status["lastFinish"] = None
        return


status = load_data()

updateStatus()
save_data(status)


@app.route('/')
def hello_world():
    return render_template('index.html')


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


@app.route("/reset", methods=["POST"])
def reset():
    print(status)
    if request.form["reset"] == "2465":
        status["lastFinish"] = None
        status["finishOrder"] = []
        for i in status["helixes"].keys():
            status["helixes"][i]["finished"] = False
        updateStatus()
        return "OK"
    return "NOK"