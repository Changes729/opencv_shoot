from flask import Flask, request, jsonify
import json
from flask_cors import CORS
app = Flask(__name__)
CORS(app, supports_credentials=True)

shoot = False

data = [
    {"active": False, "x": 0, "y": 0},
    {"active": False, "x": 0, "y": 0},
    {"active": False, "x": 0, "y": 0}
]
@app.route('/')
def hello_world():
    global data
    return json.dumps(data)


@app.route('/setpoint', methods=["POST"])
def set_point():
    global data
    text =bytes.decode(request.data, encoding='utf-8')
    data = json.loads(text)
    return "0"


@app.route('/shoot')
def shoot():
    print("shoot")
    global shoot
    shoot = True
    return "0"


@app.route('/isShoot')
def isShoot():
    global shoot
    if shoot:
        shoot = not shoot
        return "True"
    return str(shoot)    




app.run(host="0.0.0.0")
