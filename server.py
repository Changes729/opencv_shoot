from flask import Flask, request, jsonify
import json
from flask_cors import CORS
from setting import *
import main.initPoint as main
import threading

app = Flask(__name__)
CORS(app, supports_credentials=True)

shoot = False

@app.route('/')
def send_infos():
    points = main.shoot_points
    json_file = {"totalIndex": 0, "infos": []}
    for i in range(len(points)):
        for p in points[i]:
            json_file["infos"].append({
                "index": json_file["totalIndex"],
                "position": p,
                "camera": i,
                "shoot": False,
            })
            json_file["totalIndex"] += 1
    return json.dumps(json_file)


@app.route('/shoot')
def shoot():
    return json.dumps({})


@app.route('/shoot', methods=["POST"])
def set_point():
    index = request.form.get('index')     # 获取 JSON 数据
    shoot = request.form.get('shoot')
    return "0"


if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)).start()
    main.main()