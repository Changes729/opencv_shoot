import numpy as np
import cv2
import copy
import requests
width = 960
height = 480
url='http://127.0.0.1:5000/setpoint'


def dectectCorner(hull):
    xp = []
    yp = []
    for i in range(4):
        xp.append(hull[i][0][0])
        yp.append(hull[i][0][1])
    xp.sort(reverse=False)
    yp.sort(reverse=False)
    for i in range(4):
        x_index = xp.index(hull[i][0][0])
        y_index = yp.index(hull[i][0][1])
        if(x_index <= 1 and y_index <= 1):
            p1 = [hull[i][0][0], hull[i][0][1]]
        elif(x_index <= 1 and y_index >= 2):
            p2 = [hull[i][0][0], hull[i][0][1]]
        elif(x_index >= 2 and y_index >= 2):
            p3 = [hull[i][0][0], hull[i][0][1]]
        elif(x_index >= 2 and y_index <= 1):
            p4 = [hull[i][0][0], hull[i][0][1]]
        try:
            newHull = [[p1], [p2],[ p3], [p4]]
        except:
            newHull = 0
    # print(newHull)
    return newHull


def getPoint(hull, img):
    # print(hull)
    pts_o = np.float32([hull[0][0], hull[1][0], hull[2][0], hull[3][0]])
    pts_d = np.float32([ [0, 0], [0, 480],[960, 480],[960, 0]])  # 这是变换之后的图上四个点的位置
    # get transform matrixq
    M = cv2.getPerspectiveTransform(pts_o, pts_d)
    # apply transformation
    dst = cv2.warpPerspective(img, M, (width, height))
    gray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    # 二值化
    ret, binary = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(
        binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(dst, contours, -1, (0, 0, 255), 3)

    # 轮廓求中心点
    dst_centers = []
    for contour in contours:
        try:
            M = cv2.moments(contour)
            center_x = int(M["m10"] / M["m00"])
            center_y = int(M["m01"] / M["m00"])
            if(center_x/width < 0.1 and center_y/height < 0.1):
                pass
            elif(center_x/width > 0.9 and center_y/height < 0.1):
                pass
            elif(center_x/width < 0.1 and center_y/height > 0.9):
                pass
            elif(center_x/width > 0.9 and center_y/height > 0.9):
                pass
            else:
                dst_centers.append([center_x, center_y])
            cv2.circle(dst, (center_x, center_y), 2, 128, -1)  # 绘制中心点
        except:
            pass
    # cv2.imshow("img", img)
    cv2.imshow('dst', dst)
    if(dst_centers):
        return [dst_centers[0][0]/width, dst_centers[0][1]/height]
    else:
        return [0,0]

cap = cv2.VideoCapture(0)
while(True):
    # capture frame-by-frame
    ret, frame = cap.read()
    frame_draw = copy.deepcopy(frame) 
    # our operation on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # 二值化
    ret, binary = cv2.threshold(gray, 220, 255, cv2.THRESH_BINARY)
    contours, hierarchy = cv2.findContours(
        binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 绘制轮廓线
    cv2.drawContours(frame_draw, contours, -1, (0, 0, 255), 3)
    # print(contours)
    # 轮廓求中心点
    centers = []
    for contour in contours:
        M = cv2.moments(contour)
        # print(M)
        try:
            center_x = int(M["m10"] / M["m00"])
            center_y = int(M["m01"] / M["m00"])
            centers.append([center_x, center_y])
            cv2.circle(frame_draw, (center_x, center_y), 2, 128, -1)  # 绘制中心点
        except:
            continue

    if(len(centers) == 5):
        centers = np.array(centers)
        # 寻找凸包并绘制凸包（轮廓）
        hull = cv2.convexHull(centers)
        length = len(hull)
        for i in range(length):
            cv2.line(frame_draw, tuple(hull[i][0]), tuple(
                hull[(i+1) % length][0]), (0, 255, 0), 2)
            cv2.putText(frame_draw, str(i), tuple(
                hull[i][0]), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 1)
        # np.save(r"./corner.npy", hull)
        # print(hull)
        # dectectCorner(hull)
        hull = dectectCorner(hull)
        # print(hull)
        if (hull!=0):
            point = getPoint(hull, frame)
            d={'x':point[0],'y':point[1],'start':True}
            try:
                r = requests.post(url, data=d)
            except:
                pass
        else:
            try:
                d={'x':0,'y':0,'start':False}
                r = requests.post(url, data=d)
            except:
                pass
            # print(d)
            # print(point)
    # display the resulting frame
    cv2.imshow('frame', frame_draw)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # 按q键退出
        break
# when everything done , release the capture
cap.release()
cv2.destroyAllWindows()
