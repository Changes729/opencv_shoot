#!/bin/python3
import os
import getopt
import sys
import cv2

from main.cam_scan import CamScan
from main.server import server
import setting

CUR_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"

def main():
    argv = sys.argv[1:]

    try:
      opts, args = getopt.getopt(argv, "",
                                  ["init",
                                   "visual",
                                   "server",
                                   "test"])
      for opt, arg in opts:
          if opt in ['--init']:
            CamScan(setting.CAMERA_COUNT, DEBUG = setting.DEBUG).init()
          elif opt in ['--visual']:
            CamScan(setting.CAMERA_COUNT, DEBUG = setting.DEBUG).run()
          elif opt in ['--server']:
            server(setting.SERVER_PORT, None, setting.PLAYER).run()
          elif opt in ['--test']:
            hull_img = cv2.imread(CUR_PATH + "./resource/full_test-2.jpg")
            p_img = cv2.imread(CUR_PATH + "./resource/single_test-3.jpg")
            cam = CamScan(setting.CAMERA_COUNT, DEBUG = setting.DEBUG, hull_img = hull_img, p_img = p_img)
            server(setting.SERVER_PORT, cam, setting.PLAYER).run()
            cam.init()
            cam.run()
          return
    except Exception as e:
        # 异常处理块，处理捕获到的异常
        print(f"An exception occurred: {str(e)}")

    cam = CamScan(setting.CAMERA_COUNT, DEBUG = setting.DEBUG)
    server(setting.SERVER_PORT, cam, setting.PLAYER).run()
    cam.run()

if __name__ == "__main__":
  main()