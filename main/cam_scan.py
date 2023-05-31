#!/bin/python3
# ** 这个代码是用来初始化点位的
import os
import numpy as np
import cv2
from main.helper import *

## ** Defines part ***************************************************#
CURR_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"
NPY_FILE = CURR_PATH + "../cache/corner{index}.npy"

SCR_WIDTH = int(1920 / 2)
SCR_HEIGHT = int(1080 / 2)

class CamScan():
    shoot_points_px = [[0, 0]]
    shoot_points = [[0, 0]]

    def __init__(self, CAM_COUNT, cam_index_list = None, DEBUG = False, hull_img = None, p_img = None):
        if(cam_index_list == None):
            cam_index_list = np.arange(CAM_COUNT)
        self.CAM_COUNT = CAM_COUNT
        self.cam_list = cam_index_list
        self.hull = []
        self.DEBUG = DEBUG
        self.hull_img = hull_img
        self.p_img = p_img

    ## ** Functions part *************************************************#
    def get_shoot_points(self):
        return self.shoot_points

    # ** 这里需要模糊是考虑点太小无法成圈
    def gary_img(self, img):
        ksize = 0
        if(ksize == 0):
            gary = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gary = cv2.medianBlur(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), ksize)

        if (self.DEBUG):
            cv2.imshow("media", cv2.resize(gary, (SCR_WIDTH, SCR_HEIGHT)))

        return gary


    def binarization(self, gary_img, revert = False):
        _, bin = cv2.threshold(gary_img, 55 if not revert else 200,
                               255, cv2.THRESH_BINARY if not revert else cv2.THRESH_BINARY_INV)
        cv2.dilate(bin, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10)))
        if (self.DEBUG):
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
    def centroids(self, binary_img):
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


    def cal_hull(self, centers_points):
        return cv2.convexHull(np.array(centers_points))

    #** 如果凸包不是四点，就会出错，但这个错误应该在外部完成
    def get_center_point(self, hull, img):
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
            img = cv2.circle(img, p, 40, (0, 0, 0), -1)
        dst = cv2.warpPerspective(img, M, (SCR_WIDTH, SCR_HEIGHT))
        gray = self.gary_img(dst)
        centers_list = self.centroids(self.binarization(gray))

        if (self.DEBUG):
            cv2.imshow("gray", cv2.resize(gray, (SCR_WIDTH, SCR_HEIGHT)))
            log_info(centers_list)

            for center in centers_list:
                cv2.circle(dst, center, 2, 128, -1)  # 绘制中心点
            cv2.imshow('dst', dst)

        return centers_list


    def show_hulls(self, img, points, hulls):
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

    #** 现在主要是根据距离0点距离进行匹配
    def trace_points(self, old_points, curr_points):
        temp = []
        for p in curr_points:
            temp.append([np.linalg.norm(p), p])

        temp.sort()
        ret = []
        for p in temp:
            ret.append(p[1])

        log_info(ret)
        return ret

    def init(self):

        for i in range(self.CAM_COUNT):
            cam = cv2.VideoCapture(self.cam_list[i])
            err, frame = cam.read()
            if (err != True):
                log_err(err)
                continue

            #** Debug **#
            if self.hull_img is not None:
                frame = self.hull_img

            centers_list = self.centroids(self.binarization(self.gary_img(frame)))
            hull = []
            if (len(centers_list) > 4):
                hull = self.cal_hull(centers_list)

            if (len(hull) == 4):
                np.save(NPY_FILE.format(index = i), hull)
            else:
                log_err("hull {index} load failed.".format(index = i))

            cam.release()

        if(self.DEBUG):
            cv2.waitKey(0)

        cv2.destroyAllWindows()


    def run(self):
        # ** Init ********************************************************
        for i in range(self.CAM_COUNT):
            self.hull.append(np.load(NPY_FILE.format(index = i)))

        cams = []
        for i in range(self.CAM_COUNT):
            cams.append(cv2.VideoCapture(self.cam_list[i]))

        # ** Loop ********************************************************
        while (True):
            for i in range(self.CAM_COUNT):
                err, frame = cams[i].read()
                if (err != True):
                    log_err(err)
                    cams[i].release()
                    cams[i] = cv2.VideoCapture(self.cam_list[i])
                    continue

                #** Debug **#
                if self.p_img is not None:
                    frame = self.p_img

                centers_list = self.centroids(self.binarization(self.gary_img(frame)))

                if (len(centers_list) > 0):
                    new_points = self.get_center_point(self.hull[i], frame)
                    self.shoot_points_px[i] = self.trace_points(self.shoot_points_px[i], new_points)
                    if(len(self.shoot_points_px[i]) > 0 and len(self.shoot_points_px[i][0]) == 2):
                        self.shoot_points[i] = (self.shoot_points_px[i] / np.array([[960, 480]])).tolist()
                    else:
                        log_err("point size is not 2")
                        self.shoot_points[i] = [0, 0]

            if cv2.waitKey(1) and (0xFF == ord('q')):
                break

        # ** End ********************************************************
        for i in range(self.CAM_COUNT):
            cams[i].release()
        cv2.destroyAllWindows()
