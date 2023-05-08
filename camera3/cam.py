import json
import numpy as np
import cv2
import copy
import requests
cap0 = cv2.VideoCapture(0)
cap1 = cv2.VideoCapture(2)
cap2 = cv2.VideoCapture(1)
url = 'http://127.0.0.1:5000/setpoint'
hull0 = np.load(r"./corner0.npy")
hull1 = np.load(r"./corner1.npy")
hull2 = np.load(r"./corner2.npy")
width = 1080
height = 540
data = [
    {"active": False, "x": 0, "y": 0},
    {"active": False, "x": 0, "y": 0},
    {"active": False, "x": 0, "y": 0}
]
caps = [
    cap0,
    cap1,
    cap2
]
hulls = [
    hull0,
    hull1,
    hull2

]


def detectPoint(i):
    ret, frame = caps[i].read()
    pts_o = np.float32([hulls[i][0][0], hulls[i][1][0],
                       hulls[i][2][0], hulls[i][3][0]])
    pts_d = np.float32([[0, 0], [0, height], [width, height], [width, 0]])
    M = cv2.getPerspectiveTransform(pts_o, pts_d)
    dst = cv2.warpPerspective(frame, M, (width, height))
    gray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    # 二值化
    ret, binary = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(
        binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(dst, contours, -1, (0, 0, 255), 3)
    dst_centers = []
    for contour in contours:
        try:
            M = cv2.moments(contour)
            center_x = int(M["m10"] / M["m00"])
            center_y = int(M["m01"] / M["m00"])
            dst_centers.append([center_x, center_y])
            cv2.circle(dst, (center_x, center_y), 2, 128, -1)  # 绘制中心点
        except:
            pass
    # print([dst_centers[0][0]/width, dst_centers[0][1]/height])
    cv2.imshow('dst'+str(i), dst)
    if(len(dst_centers) == 1):
        data[i]['active'] = True
        data[i]['x'] = dst_centers[0][0]/width
        data[i]['y'] = dst_centers[0][1]/height
    else:
        data[i]['active'] = False


while(1):
    detectPoint(0)
    detectPoint(1)
    detectPoint(2)
    print(data)
    data1 = json.dumps(data)
    r = requests.post(url, data=data1)
    if cv2.waitKey(1) & 0xFF == ord('q'):  # 按q键退出
        break

cap0.release()
# cap2.release()
cv2.destroyAllWindows()
