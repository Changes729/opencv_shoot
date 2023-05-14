from flask import Flask, request, jsonify
import json
from flask_cors import CORS
import threading


class server():
    shoot = [False, False]
    app = Flask(__name__)

    def __init__(self, port, cam_scan, players):
        CORS(self.app, supports_credentials=True)
        self.cam_scan = cam_scan
        self.port = port
        self.players = players

    @app.route('/aim_info')
    def send_infos(self):
        points = self.cam_scan.get_shoot_points() if self.cam_scan != None else []
        json_file = {"totalIndex": 0, "infos": []}
        for i in range(len(points)):
            for p in points[i]:
                json_file["infos"].append({
                    "index": json_file["totalIndex"],
                    "position": p,
                    "camera": i,
                })
                json_file["totalIndex"] += 1
                self.shoot = [False, False]
        return json.dumps(json_file)

    @app.route('/shoot')
    def trigger_shoot(self):
        print(request.remote_addr)
        for i in range(len(self.players)):
            if(self.players[i] == request.remote_addr):
                self.shoot[i] = True
        return json.dumps({})


    @app.route('/shoot_info')
    def shoot_info(self):
        return json.dumps({"shoot": self.shoot})

    def app_run(self):
        self.app.run(host="0.0.0.0",
                        port=self.port,
                        debug=False,
                        use_reloader=False)

    def run(self, use_thread = True):
        if use_thread:
            threading.Thread(target=self.app_run).start()
        else:
            self.app_run()
