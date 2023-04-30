import cv2
import numpy as np
import time

drawing = False
ix, iy = -1, -1
global roi

def mouse_callback(event, x, y, flags, param):
    global ix, iy, drawing, roi

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = img.copy()
            cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow('image', img_copy)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        x, y = max(ix, x), max(iy, y)
        roi = img[iy:y, ix:x]
        cv2.destroyAllWindows()


img = cv2.imread('img/img_1.jpg')



cv2.namedWindow('image')
cv2.setMouseCallback('image', mouse_callback)

start_time = time.time()
cv2.imshow('image', img)
cv2.waitKey(0)



cv2.imwrite('roi.png', roi)
print('ROI saved to roi.jpg')


start_time = time.time()
img_rgb = img
img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

template = cv2.imread('roi.png', 0)

#тут надо попробовать вращать

w, h = template.shape[::-1]
res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
threshold = 0.7
loc = np.where(res >= threshold)

for pt in zip(*loc[::-1]):
    cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 255, 255), 2)

end_time = time.time()
elapsed_time = end_time - start_time

print(f"Время выполнения программы: {elapsed_time:.2f} секунд")
cv2.imshow('Detected', img_rgb)
cv2.waitKey(0)



