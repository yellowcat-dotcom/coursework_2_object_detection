import numpy
import cv2
import imutils  #позволяет подсчитывать кол-во контуров
import time

image =cv2.imread("img/img_2.jpg")
start_time = time.time()
gray=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

#упрощаем изображение наложением блюра по гауссу
gray=cv2.GaussianBlur(gray, (1,1),0)
#выделение активных зон МЕНЯТЬ ВТОРОЙ ПАРАМЕТР 100
edges=cv2.Canny(gray, 300, 650)

#Создаем закрытие для шума с помощью ядра МЕНЯТЬ ПАРАМЕТР (10,10)
kernel=cv2.getStructuringElement(cv2.MORPH_RECT, (1,1))

closed=cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
cv2.imshow("airplane_137.jpg", closed)
cv2.waitKey(0)
#поиск контуров
cnts=cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts=imutils.grab_contours(cnts)


total=0
for c in cnts:
    p=cv2.arcLength(c,True)
    approx=cv2.approxPolyDP(c, 0.02*p,True)
    cv2.drawContours(image, [approx], -1, (0, 255), 4)
    total+=1


end_time = time.time()
elapsed_time = end_time - start_time
print(f"Время выполнения программы: {elapsed_time:.2f} секунд")
cv2.imshow("otvet", image)
cv2.waitKey(0)