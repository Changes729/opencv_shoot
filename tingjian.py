#!/bin/python3
import os
import getopt
import sys

from main.cam_scan import CamScan
from main.server import server
import setting

CUR_PATH = os.path.dirname(os.path.abspath(__file__))

def main():
    argv = sys.argv[1:]

    try:
      opts, args = getopt.getopt(argv, "",
                                  ["init",
                                   "visual",
                                   "server"])
      for opt, arg in opts:
          if opt in ['--init']:
            CamScan(setting.CAMERA_COUNT, DEBUG = setting.DEBUG).init()
          elif opt in ['--visual']:
            CamScan(setting.CAMERA_COUNT, DEBUG = setting.DEBUG).run()
          elif opt in ['--server']:
            server(setting.SERVER_PORT, None, setting.PLAYER).run()
          return
    except:
        print("Error")

    cam = CamScan(setting.CAMERA_COUNT, DEBUG = setting.DEBUG)
    server(setting.SERVER_PORT, cam, setting.PLAYER).run()
    cam.run()

if __name__ == "__main__":
  main()