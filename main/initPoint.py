#!/bin/python3
# ** 这个代码是用来初始化点位的
import os
import numpy as np
import cv2
import requests
import math
from enum import Enum

## ** Defines part ***************************************************#
CURR_PATH = os.path.dirname(os.path.abspath(__file__))
NPY_FILE = CURR_PATH + "/corner.npy"
DEPTH_CHART = CURR_PATH + '/../test1.jpg'
DEBUG_ENABLE = True
NUMPY_EXPORT = False


class CAM(Enum):
    FRONT_CAM = 0
    LEFT_CAM = 1
    RIGHT_CAM = 2

    TOTAL_CAM = 1


SCR_WIDTH = int(1920 / 2)
SCR_HEIGHT = int(1080 / 2)

shoot_points = [[0, 0]]

## ** Functions part *************************************************#
def log_err(info):
    print("[err]", info)

# ** 这里需要模糊是考虑点太小无法成圈
def gary_img(img):
    gary = cv2.medianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), 31)

    if (DEBUG_ENABLE):
        cv2.imshow("media", cv2.resize(gary, (SCR_WIDTH, SCR_HEIGHT)))

    return gary


def binarization(gary_img, revert = False):
    _, bin = cv2.threshold(gary_img, 55, 255, cv2.THRESH_BINARY if not revert else cv2.THRESH_BINARY_INV)

    if (DEBUG_ENABLE):
        cv2.imshow("bin", cv2.resize(bin, (SCR_WIDTH, SCR_HEIGHT)))

    return bin

# ** 这是计算多个轮廓中心的
# ** 主要原理是通过 findContours 画出等高线轮廓；然后通过 moments 计算中心
# ** 这里先解释如何计算重心，这里用到了计算机图形的 原始矩 的概念
# ** 原始矩的概念不需要硬记，可以从微积分中的重心计算去理解它：
# ** ———— 某个图形对x的积分除以图形面积，得到x的重心；y同理
# ** 如果你还想理解矩是如何计算重心的，第二步，你需要离散的看待微积分计算过程，并带入计算机
# ** ———— 其实计算机中的数组已经是微元了，只需要加起来就是积分了
# ** 第三步，你需要理解什么是矩，什么是一阶矩等概念
# ** ———— 矩需要从矩阵的概念去理解，矩阵是xy的离散函数，当我们对矩阵进行累加时，xy不赋权，则结果是总面积
# ** ———— 当我们对x赋权时，就是计算x上的质量分布（就有矩了，这里看不懂再联系一下力矩的概念）
# ** 回到这个算法，m10 / m00 事实上就是对 x 的一阶矩除以 面积（零阶矩），得到x的重心，
# ** m01 / m00 同理；
# ** 因为要计算重心，所以事实上需要知道一个「识别点」的数据，这里使用等高线来获取某个识别点的所有元素：
# ** ———— RETR_TREE：会建立完整的父子关系
# ** ———— CHAIN_APPROX_SIMPLE: 算法压缩
# ** 这样 moments 获取到的是压缩过的向量数组
def centroids(binary_img):
    contours, _ = cv2.findContours(
        binary_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 轮廓求中心点
    centers = []
    for contour in contours:
        M = cv2.moments(contour)
        if (M["m00"]):
            center_x = int(M["m10"] / M["m00"])
            center_y = int(M["m01"] / M["m00"])
            centers.append([center_x, center_y])
        else:
            log_err("m00 is 0")

    return centers


def cal_hull(centers_points):
    return cv2.convexHull(np.array(centers_points))

#** 如果凸包不是四点，就会出错，但这个错误应该在外部完成
def get_center_point(hull, img):
    ret_source = hull[:4, 0, :]
    ret_destiny = np.array([[0, 0], [960, 0], [960, 480], [0, 480]])

    min = 0
    for i in range(1, len(ret_source)):
        if np.linalg.norm(ret_source[i]) < np.linalg.norm(ret_source[min]):
            min = i
    ret_source = np.roll(ret_source, -min, axis=0)

    pts_o = np.float32(ret_source)
    pts_d = np.float32(ret_destiny)
    M = cv2.getPerspectiveTransform(pts_o, pts_d)

    for p in ret_source:
        gray = cv2.circle(img, p, 25, (255, 255, 255), -1)
    dst = cv2.warpPerspective(img, M, (SCR_WIDTH, SCR_HEIGHT))
    gray = gary_img(dst)
    centers_list = centroids(binarization(gray, True))

    if (DEBUG_ENABLE):
        cv2.imshow("gray", cv2.resize(gray, (SCR_WIDTH, SCR_HEIGHT)))
        print(centers_list)

        for center in centers_list:
            cv2.circle(dst, center, 2, 128, -1)  # 绘制中心点
        cv2.imshow('dst', dst)

    return centers_list


def show_hulls(img, points, hulls):
    img_lookup = img.copy()
    for point_center in points:
        r = 2
        color = (0, 0, 128)
        cv2.circle(img_lookup, point_center, r,
                   color, cv2.FILLED)
    length = len(hulls)
    for i in range(length):
        cv2.line(img_lookup, tuple(hulls[i][0]), tuple(
            hulls[(i+1) % length][0]), (0, 255, 0), 2)
        cv2.putText(img_lookup, str(i), tuple(
            hulls[i][0]), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 1)

    cv2.imshow("hull",  cv2.resize(img_lookup, (SCR_WIDTH, SCR_HEIGHT)))


def main():
    # ** Init ********************************************************
    cams = []
    for i in range(CAM.TOTAL_CAM.value):
        cams.append(cv2.VideoCapture(i))

    # ** Loop ********************************************************
    while (True):
        for i in range(CAM.TOTAL_CAM.value):
            err, frame = cams[i].read()
            if (err != True):
                log_err(err)
                continue

            centers_list = centroids(binarization(gary_img(frame)))
            hull = []
            if (len(centers_list) > 4):
                hull = cal_hull(centers_list)

            if (len(hull) == 4):
                global shoot_points
                shoot_points[i] = get_center_point(hull, frame)
                shoot_points[i] = (shoot_points[i] / np.array([[960, 480]])).tolist()
            else:
                log_err("hull is " + str(len(hull)) + "points")

            if (NUMPY_EXPORT):
                np.save(NPY_FILE, hull)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # ** End ********************************************************
    for i in range(CAM.TOTAL_CAM.value):
        cams[i].release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
