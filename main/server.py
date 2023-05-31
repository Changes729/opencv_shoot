from flask import Flask, Response, request, jsonify
import json
from flask_cors import CORS
import threading
import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

class server(object):
    shoot = [False, False]
    app = Flask(__name__)

    def __init__(self, port, cam_scan, players):
        CORS(self.app, supports_credentials=True)
        self.cam_scan = cam_scan
        self.port = port
        self.players = players

    def send_infos(self):
        points = self.cam_scan.get_shoot_points() if self.cam_scan != None else []
        json_file = {"totalIndex": 0, "infos": []}
        for i in range(len(points)):
            for p in points[i]:
                if(type(p) is not int and len(p) == 2):
                    json_file["infos"].append({
                        "index": json_file["totalIndex"],
                        "position": p,
                        "camera": i,
                    })
                    json_file["totalIndex"] += 1
        self.shoot = [False, False]
        return jsonify(json_file)

    def trigger_shoot(self):
        print(request.remote_addr)
        for i in range(len(self.players)):
            if(self.players[i] == request.remote_addr):
                self.shoot[i] = True
        return jsonify({})


    def shoot_info(self):
        return jsonify({"shoot": self.shoot})

    def add_endpoint(self, endpoint : str, endpoint_name=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, handler)

    def app_run(self):
        self.add_endpoint(endpoint='/aim_info', endpoint_name='aim_info', handler=self.send_infos)
        self.add_endpoint(endpoint='/shoot', endpoint_name='shoot', handler=self.trigger_shoot)
        self.add_endpoint(endpoint='/shoot_info', endpoint_name='shoot_info', handler=self.shoot_info)
        self.app.run(host="0.0.0.0",
                        port=self.port,
                        debug=False,
                        use_reloader=False)


    def run(self, use_thread = True):
        if use_thread:
            threading.Thread(target=self.app_run).start()
        else:
            self.app_run()
