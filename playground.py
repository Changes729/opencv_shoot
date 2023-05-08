import cv2

retval = cv2.imread("./test.jpg")
cv2.imshow("demo", retval)
key = cv2.waitKey()
cv2.imwrite("write.bmp",retval)
cv2.destroyAllWindows()
