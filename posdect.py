import numpy as np
import cv2
img = cv2.imread('./22.png')
# img = cv2.medianBlur(img, 5)
h1, w1 = img[:, :, 0].shape
img_draw = cv2.imread('./test1.jpg')
# 获取灰度图像
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# 二值化
ret, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

contours, hierarchy = cv2.findContours(
    binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# 绘制轮廓线
# cv2.drawContours(img_draw, contours, -1, (0, 0, 255), 3)

# 轮廓求中心点
centers = []
for contour in contours:
    M = cv2.moments(contour)
    center_x = int(M["m10"] / M["m00"])
    center_y = int(M["m01"] / M["m00"])
    centers.append([center_x, center_y])
    cv2.circle(img_draw, (center_x, center_y), 2, 128, -1)  # 绘制中心点

centers = np.array(centers)
# 寻找凸包并绘制凸包（轮廓）
hull = cv2.convexHull(centers)
length = len(hull)
for i in range(length):
    cv2.line(img_draw, tuple(hull[i][0]), tuple(
        hull[(i+1) % length][0]), (0, 255, 0), 2)
    cv2.putText(img_draw, str(i), tuple(
        hull[i][0]), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 1)

pts_o = np.float32([hull[0][0], hull[1][0], hull[2][0], hull[3][0]])
pts_d = np.float32([[960, 480], [0, 480], [0, 0], [960, 0]]) # 这是变换之后的图上四个点的位置
# get transform matrix
M = cv2.getPerspectiveTransform(pts_o, pts_d)
# apply transformation
dst = cv2.warpPerspective(img, M, (960, 480)) 


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
    dst_centers.append([center_x, center_y])
    cv2.circle(dst, (center_x, center_y), 2, 128, -1)  # 绘制中心点

print(dst_centers)

cv2.imshow("img", img_draw)
cv2.imshow('dst', dst)

cv2.waitKey(0)
cv2.destroyAllWindows()
