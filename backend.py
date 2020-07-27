from flask import Flask, jsonify, request
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
    for h in status["helixes"]:
        if h["completed"]:
            status["finished"] += 1
    status["progress"] = (100*status["finished"]) / status["helix_count"]


def finishHelix(h):
    

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
    print(request.data)
    return request.form