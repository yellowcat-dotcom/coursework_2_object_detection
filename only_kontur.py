import numpy
import cv2
import imutils  #позволяет  подсчитывать кол-во контуров

image =cv2.imread("airplane_017.jpg")
gray=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#упрощаем изображение наложением блюра по гауссу
gray=cv2.GaussianBlur(gray, (3,3),0)
#выделение активных зон МЕНЯТЬ ВТОРОЙ ПАРАМЕТР 100
edges=cv2.Canny(gray, 10, 500)
#cv2.imshow("airplane_137.jpg", edges)
# cv2.imshow("airplane_137.jpg", edges)
#Создаем закрытие для шума с помощью ядра МЕНЯТЬ ПАРАМЕТР (10,10)
kernel=cv2.getStructuringElement(cv2.MORPH_RECT, (10,10))
closed=cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

#поиск контуров
cnts=cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts=imutils.grab_contours(cnts)


total=0
for c in cnts:
    p=cv2.arcLength(c,True)
    approx=cv2.approxPolyDP(c, 0.02*p,True)
    print(approx)

    cv2.drawContours(image, [approx], -1, (0, 255), 4)
    total+=1
    #if len(approx)==4:
        #cv2.drawContours(image, [approx], -1, (0,255),4)
        #total+=1
print(total)

cv2.imshow("airplane_137.jpg", image)
cv2.waitKey(0)