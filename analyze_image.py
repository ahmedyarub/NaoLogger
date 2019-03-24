import cv2
import numpy as np

def window_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONUP:
        tmp_img = cv2.cvtColor(src_img, cv2.COLOR_RGB2HSV)

        print '\tRGB: ', np.array2string(src_img[y, x])
        print '\tHSV: ', np.array2string(tmp_img[y, x])


src_img = cv2.imread('P2.jpg')
dst_img = cv2.cvtColor(src_img, cv2.COLOR_RGB2HSV)

lower_color = np.array([88, 70, 253])
upper_color = np.array([92, 190, 255])

mask = cv2.inRange(dst_img, lower_color, upper_color)
imask = mask > 0

filtered = np.zeros_like(src_img, np.uint8)
filtered[imask] = src_img[imask]

imgray = cv2.cvtColor(filtered, cv2.COLOR_BGR2GRAY)
ret, thresh = cv2.threshold(imgray, 1, 255, 0)
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

c = max(contours, key = cv2.contourArea)

x, y, w, h = cv2.boundingRect(c)
thresh = thresh[y:y+h, x:x+w]
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

contours.remove(max(contours, key = cv2.contourArea))
c = max(contours, key = cv2.contourArea)

print cv2.contourArea(c)
M = cv2.moments(c)
height, width, channels = src_img.shape
print (float(M['m10']/M['m00'])+x) / width
print (float(M['m01']/M['m00'])+y) / height
cv2.drawContours(src_img, c, -1, (0, 0, 255), 3, offset=(x,y))

cv2.imshow("image", src_img)
cv2.setMouseCallback("image", window_click)
cv2.waitKey(0)
cv2.destroyAllWindows()
#
# imgray = mask
# ret, thresh = cv2.threshold(imgray, 127, 255, 0)
# contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
#
# if len(contours) != 0:
#     c = max(contours, key=cv2.contourArea)
#     x, y, w, h = cv2.boundingRect(c)
#     cv2.rectangle(src_img, (x, y), (x + w, y + h), (255, 0, 0), 3)
#     cv2.imshow('filtered', filtered)
