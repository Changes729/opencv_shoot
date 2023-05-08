import numpy as np
import cv2

width = 960
height = 480

def getPoint(hull, img):
    pts_o = np.float32([hull[0][0], hull[1][0], hull[2][0], hull[3][0]])
    pts_d = np.float32([[960, 480], [0, 480], [0, 0],
                        [960, 0]])  # 这是变换之后的图上四个点的位置
    # get transform matrix
    M = cv2.getPerspectiveTransform(pts_o, pts_d)
    # apply transformation
    dst = cv2.warpPerspective(img, M, (width, height))

    gray = cv2.cvtColor(dst, cv2.COLOR_BGR2GRAY)
    # 二值化
    ret, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(
        binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    cv2.drawContours(dst, contours, -1, (0, 0, 255), 3)

    # 轮廓求中心点
    dst_centers = []
    for contour in contours:
        M = cv2.moments(contour)
        center_x = int(M["m10"] / M["m00"])
        center_y = int(M["m01"] / M["m00"])
        if(center_x/width<0.2 and center_y/height<0.2):
          pass
        elif(center_x/width>0.98 and center_y/height<0.2):
          pass
        elif(center_x/width<0.2 and center_y/height>0.98):
          pass
        elif(center_x/width>0.98 and center_y/height>0.98):
          pass
        else:
          dst_centers.append([center_x, center_y])
        cv2.circle(dst, (center_x, center_y), 2, 128, -1)  # 绘制中心点
    # cv2.imshow("img", img)
    # cv2.imshow('dst', dst)
    return [dst_centers[0][0]/width,dst_centers[0][1]/height]



hull = np.load(r"./corner.npy")
# print(hull)
img = cv2.imread('../test2.jpg')
print(getPoint(hull,img))

cv2.waitKey(0)
cv2.destroyAllWindows()


