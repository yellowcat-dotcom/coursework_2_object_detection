import cv2
import numpy as np
import time

# Устанавливаем начальные значения для рисования прямоугольника
drawing = False
ix, iy = -1, -1
# Создаем переменную для хранения выделенной области изображения
global roi

# Функция, которая будет вызываться при каждом событии мыши на изображении
def mouse_callback(event, x, y, flags, param):
    global ix, iy, drawing, roi

    # Если нажата левая кнопка мыши, начинаем рисовать прямоугольник
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix, iy = x, y

    # Если мышь двигается, рисуем текущий прямоугольник
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img_copy = img.copy()
            cv2.rectangle(img_copy, (ix, iy), (x, y), (0, 255, 0), 2)
            cv2.imshow('image', img_copy)

    # Если отпущена левая кнопка мыши, сохраняем выделенную область и закрываем окно
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        x, y = max(ix, x), max(iy, y)
        roi = img[iy:y, ix:x]
        cv2.destroyAllWindows()


# Загружаем изображение
img = cv2.imread("img/img_1.jpg")
#img = cv2.imread("img.png")

# Создаем окно и назначаем функцию обратного вызова для событий мыши на окне
cv2.namedWindow('image')
cv2.setMouseCallback('image', mouse_callback)

# Показываем изображение и ждем нажатия клавиши
cv2.imshow('image', img)
cv2.waitKey(0)
#####
start_time = time.time()
# Сохраняем выделенную область в файл roi.png
cv2.imwrite('roi.png', roi)
print('ROI saved to roi.jpg')

# Создаем копии изображения: цветную и черно-белую
img_rgb = img
img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)

# Загружаем шаблон, который мы выделили ранее, и находим его размеры
template = cv2.imread('roi.png', 0)

#                   тут надо попробовать вращать

w, h = template.shape[::-1]
# Ищем шаблон на изображении
res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
# Устанавливаем пороговое значение и получаем координаты найденных совпадени
threshold = 0.7
loc = np.where(res >= threshold)

# Для каждого найденного совпадения находим контуры объектов и рисуем их на исходном изображении
for pt in zip(*loc[::-1]):

    img_gray_copy = img_gray.copy()
    roi_gray = img_gray_copy[pt[1]:pt[1] + h, pt[0]:pt[0] + w]
    # бинаризация изображения и нахождение контуров
    _, thresh = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # рисуем контуры на исходном изображении
    for cnt in contours:
        cnt = cnt + np.array([pt[0], pt[1]])  # сдвигаем контур на координаты области интереса
        cv2.drawContours(img_rgb, [cnt], 0, (0, 0, 255), 2)

cv2.imshow('Detected', img_rgb)
cv2.imwrite('Detected.png', img_rgb)
end_time = time.time()
elapsed_time = end_time - start_time

print(f"Время выполнения программы: {elapsed_time:.2f} секунд")
cv2.waitKey(0)
