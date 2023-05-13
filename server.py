from flask import Flask, request, jsonify
import json
from flask_cors import CORS
from setting import *
import main.initPoint as main
import threading

app = Flask(__name__)
CORS(app, supports_credentials=True)

deviceIP = ["192.168.199.127", ""]
shoot = [False, False]

@app.route('/')
def send_infos():
    global shoot
    points = main.shoot_points
    json_file = {"totalIndex": 0, "infos": []}
    for i in range(len(points)):
        for p in points[i]:
            json_file["infos"].append({
                "index": json_file["totalIndex"],
                "position": p,
                "camera": i,
            })
            json_file["totalIndex"] += 1
            shoot = [False, False]
    return json.dumps(json_file)


@app.route('/shoot')
def trigger_shoot():
    print(request.remote_addr)
    for i in range(len(deviceIP)):
        if(deviceIP[i] == request.remote_addr):
            shoot[i] = True
    return json.dumps({})


@app.route('/shoot_info')
def shoot_info():
    return json.dumps({"shoot": shoot})

if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)).start()
    main.main()