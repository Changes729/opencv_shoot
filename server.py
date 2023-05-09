from flask import Flask, request, jsonify
import json
from flask_cors import CORS
from setting import *
app = Flask(__name__)
CORS(app, supports_credentials=True)

x = 0
y = 0
shoot = False
start = False


@app.route('/')
def hello_world():
    global x, y, shoot, start
    if shoot:
        shoot = not shoot
        return json.dumps({"x": x, "y": y, 'shoot': True, 'start': start})
    if start:
        start = not start
        return json.dumps({"x": x, "y": y, 'shoot': shoot, 'start': True})
    # print(x,y)
    return json.dumps({"x": x, "y": y, 'shoot': shoot, 'start': start})


@app.route('/setpoint', methods=["POST"])
def set_point():
    global x, y, start
    x = request.form.get('x')     # 获取 JSON 数据
    y = request.form.get('y')
    start = request.form.get('start')
    return "0"


@app.route('/shoot')
def shoot():
    global shoot
    shoot = True
    return json.dumps({"x": x, "y": y, 'shoot': shoot})


@app.route('/start')
def start():
    global start
    start = not start
    return json.dumps({"x": x, "y": y, 'shoot': shoot, 'start': start})


app.run(host="0.0.0.0", port=port)
