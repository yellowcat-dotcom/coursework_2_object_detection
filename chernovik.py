from tkinter import *
from PIL import ImageTk, Image
from tkinter import filedialog
import cv2
import numpy as np
from tkinter import messagebox
import imutils
import time


root = Tk()

drawing = False
ix, iy = -1, -1
global roi

immm = ''
img_prewitt = ''
img_canny = ''
label_1 = ''
label_2 = ''
label_3 = ''
label_4 = ''

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
def detect_template_in_image(image_path):
    #на основе эталона
    start_time = time.time()
    img_rgb = cv2.imread(image_path)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread('roi.png', 0)
    for i in range(4):
        template = cv2.rotate(template, cv2.ROTATE_90_CLOCKWISE)
        # тут надо попробовать вращать
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.7
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 255, 255), 2)
        end_time = time.time()
        elapsed_time = end_time - start_time
    return img_rgb, elapsed_time

def detect_and_draw_contours(image_path, kernel_size=(1,1), canny_thresholds=(300, 900), contour_color=(0, 255), contour_thickness=4):
    # на основе контура
    start_time = time.time()
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (1,1), 0)
    edges = cv2.Canny(gray, canny_thresholds[0], canny_thresholds[1])
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    cnts = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    total = 0
    for c in cnts:
        p = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * p, True)
        cv2.drawContours(image, [approx], -1, contour_color, contour_thickness)
        total += 1
    end_time = time.time()
    elapsed_time = end_time - start_time
    return image, elapsed_time

def detect_template_and_contours(image_path):
    #эталон и контур
    start_time = time.time()
    img_rgb = cv2.imread(image_path)
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    template = cv2.imread('roi.png', 0)
    for i in range(4):
        template = cv2.rotate(template, cv2.ROTATE_90_CLOCKWISE)

        w, h = template.shape[::-1]
        res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.7
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            img_gray_copy = img_gray.copy()
            roi_gray = img_gray_copy[pt[1]:pt[1] + h, pt[0]:pt[0] + w]

            # Адаптивная бинаризация
            # thresh = cv2.adaptiveThreshold(roi_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY_INV, blockSize=11, C=2)
            gray = cv2.GaussianBlur(roi_gray, (1, 1), 0)
            # Применение оператора Canny
            edges = cv2.Canny(gray, 300, 650)

            # Использование морфологической операции для улучшения контуров
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
            edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

            # Поиск контуров
            contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_KCOS)

            # Рисование контуров на исходном изображении
            for cnt in contours:
                cnt = cnt + np.array([pt[0], pt[1]])  # Сдвигаем контур на координаты области интереса
                cv2.drawContours(img_rgb, [cnt], 0, (0, 0, 255), 2)
    end_time = time.time()
    elapsed_time = end_time - start_time
    return img_rgb, elapsed_time

def open_img():
    #работа с начальным изображением
    x = openfilename()
    global img
    img = Image.open(x)
    img = img.resize((450, 300), Image.Resampling.LANCZOS)
    ab = ImageTk.PhotoImage(img)
    global panel
    panel = Label(root, image=ab)
    panel.image = ab
    panel.place(x=5, y=30)

    global label_1
    label_1 = Label(text="Начальное изображение")
    label_1.place(x=155, y=332)

    img = cv2.imread(x)
    cv2.namedWindow('image')
    cv2.setMouseCallback('image', mouse_callback)
    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.imwrite('roi.png', roi)
    #вывод эталона на экран
    global pane
    imgg = Image.open('roi.png')
    abb = ImageTk.PhotoImage(imgg)
    pane = Label(root, image=abb)
    pane.image = abb
    pane.place(x=980, y=50)
    global label_etalon
    label_etalon = Label(text="Эталон")
    label_etalon.place(x=980, y=32)
    #конец вывода эталона
    txt='Время выполнения:\n'
    # только эталон
    image_etalon, time_etalon = detect_template_in_image(x)
    cv2.imwrite('image_etalon.png', image_etalon)
    txt=txt+"Поиск объекта на основе \n поиска эталона"+'\n'+str(time_etalon)+'\n'
    #print("Поиск объекта на основе контуров", time_etalon)
    img_only_etalon = Image.fromarray(image_etalon)
    img_only_etalon_resize = img_only_etalon.resize((450, 300), Image.Resampling.LANCZOS)
    img_only_etalon_tk = ImageTk.PhotoImage(img_only_etalon_resize)
    global panel_img_only_etalon_tk
    panel_img_only_etalon_tk = Label(root, image=img_only_etalon_tk)
    panel_img_only_etalon_tk.image = img_only_etalon_tk
    panel_img_only_etalon_tk.place(x=505, y=30)
    global label_etalon_metod
    label_etalon_metod = Label(text="Поиск объекта на основе контуров")
    label_etalon_metod.place(x=655, y=332)

# только контур
    image_kontur, time_kountur=detect_and_draw_contours(x)
    #print("Поиск объекта на основе контуров",time_kountur)
    txt=txt+"Поиск объекта на основе контуров"+'\n'+str(time_kountur)+'\n'
    cv2.imwrite('image_kontur.png', image_kontur)
        # вывод и подпись метода на основе контура
    img_only_kontut = Image.fromarray(image_kontur)
    img_only_kontut_resize = img_only_kontut.resize((450, 300), Image.Resampling.LANCZOS)
    img_only_kontut_tk = ImageTk.PhotoImage(img_only_kontut_resize)
    global panel_img_only_kontut_tk
    panel_img_only_kontut_tk = Label(root, image=img_only_kontut_tk)
    panel_img_only_kontut_tk.image = img_only_kontut_tk
    panel_img_only_kontut_tk.place(x=5, y=380)
    global label_kontut
    label_kontut = Label(text="Поиск объекта на основе контуров")
    label_kontut.place(x=155, y=682)

    #эталон и контур
    kont_and_templ, time_kont_and_templ = detect_template_and_contours(x)
    cv2.imwrite('kont_and_templ.png', kont_and_templ)
    txt=txt+"Поиск объекта на основе эталона \n и контуров"+'\n'+str(time_kont_and_templ)
    #print("Поиск объекта на основе эталона и контуров",time_kont_and_templ)
    img_kont_and_templ = Image.fromarray(kont_and_templ)
    img_kont_and_templ_resize = img_kont_and_templ.resize((450, 300), Image.Resampling.LANCZOS)
    img_kont_and_templ_tk = ImageTk.PhotoImage(img_kont_and_templ_resize)
    global panel_img_kont_and_templ_tk
    panel_img_kont_and_templ_tk = Label(root, image=img_kont_and_templ_tk)
    panel_img_kont_and_templ_tk.image = img_kont_and_templ_tk
    panel_img_kont_and_templ_tk.place(x=505, y=380)
    global label_kont_and_templ
    label_kont_and_templ = Label(text="Поиск объекта на основе эталона и контуров")
    label_kont_and_templ.place(x=655, y=682)
    # вывод времени
    global label_time
    label_time = Label(text=txt)
    label_time.place(x=970, y=340)

def openfilename():
    filename = filedialog.askopenfilename(title='Выбор изображения')
    return filename


def remove_text():
    if label_1 != '':
        panel.destroy()
        label_1.destroy()
        label_time.destroy()
        pane.destroy()
        label_etalon.destroy()
        panel_img_only_etalon_tk.destroy()
        label_etalon_metod.destroy()
        panel_img_kont_and_templ_tk.destroy()
        label_kont_and_templ.destroy()
        panel_img_only_kontut_tk.destroy()
        label_kontut.destroy()

    else:
        messagebox.showerror(title="Ошибка", message="Необходимо выбрать изображение")


def program():
    messagebox.showinfo(title="О программе", message="""Наименование: Object search
Это приложение для выделения объектов на радиолокациооных изображениях. 
В частности в нем реализован метод на основе выделения контуров объекта 
и метод, основанный на сравнении с эталоном. 
Данные методы были совмещены в третий метод. 
Проведено сравнение методов с помощью оценки времени работы.""")


def tutorials():
    messagebox.showinfo(title="О программе", message="""Для работы приложения вам необходимо
нажать \"Выбрать изображение\" во вкладке \"Файл\".
Вы увидите на экране изображения с подписями- результат работы разных методов.
Вы можете сохранить их по отдельности.""")


def save_Sobel():
    # file = filedialog.asksaveasfilename(title = u'save file ', filetypes = files, defaultextension=files)
    if panel_img_only_kontut_tk != '':
        files = [('JPEG files', '*.jpeg'),
                 ('PNG Files', '*.png'),
                 ('Python Files', '*.py')]
        cv2.imwrite(filedialog.asksaveasfilename(title=u'save file ', filetypes=files, defaultextension=files), panel_img_only_kontut_tk)
        messagebox.showinfo(title="Информация", message="Изображение сохранено")
    else:
        messagebox.showerror(title="Ошибка", message="Необходимо выбрать изображение")
        # img.save(filedialog.asksaveasfilename(title = u'save file ', filetypes = files, defaultextension=files))


def save_prewitt():
    # file = filedialog.asksaveasfilename(title = u'save file ', filetypes = files, defaultextension=files)
    if img_prewitt != '':
        files = [('JPEG files', '*.jpeg'),
                 ('PNG Files', '*.png'),
                 ('Python Files', '*.py')]
        cv2.imwrite(filedialog.asksaveasfilename(title=u'save file ', filetypes=files, defaultextension=files),
                    img_prewitt)
        messagebox.showinfo(title="Информация", message="Изображение сохранено")

    else:
        messagebox.showerror(title="Ошибка", message="Необходимо выбрать изображение")
        # img.save(filedialog.asksaveasfilename(title = u'save file ', filetypes = files, defaultextension=files))


def save_canny():
    # file = filedialog.asksaveasfilename(title = u'save file ', filetypes = files, defaultextension=files)
    if panel_img_kont_and_templ_tk != '':
        files = [('JPEG files', '*.jpeg'),
                 ('PNG Files', '*.png'),
                 ('Python Files', '*.py')]
        cv2.imwrite(filedialog.asksaveasfilename(title=u'save file ', filetypes=files, defaultextension=files),
                    panel_img_kont_and_templ_tk)
        messagebox.showinfo(title="Информация", message="Изображение сохранено")

    else:
        messagebox.showerror(title="Ошибка", message="Необходимо выбрать изображение")
        # img.save(filedialog.asksaveasfilename(title = u'save file ', filetypes = files, defaultextension=files))


root.title("Object search")
root.geometry("1200x750")
root.resizable()
root.resizable(width=True, height=True)
root.option_add("*tearOff", FALSE)

main_menu = Menu()
file_menu = Menu()
setings_menu = Menu()

setings_menu.add_command(label="Метод на основе контуров", command=save_Sobel)  # , command = save)
setings_menu.add_command(label="Метод на основе эталона", command=save_prewitt)
setings_menu.add_command(label="Метод на основе эталона и контура", command=save_canny)

file_menu.add_command(label="Выбрать изображение", command=open_img)
file_menu.add_command(label="Удалить изображение", command=remove_text)
file_menu.add_cascade(label="Сохранить", menu=setings_menu)

main_menu.add_cascade(label="Файл", menu=file_menu)
main_menu.add_command(label="Помощь", command=tutorials)
main_menu.add_command(label="О программе", command=program)

main_menu.add_command(label="Выход", command=root.destroy)

root.config(menu=main_menu)

imgg = Image.open('fon2.png')
imgg = imgg.resize((1200, 750), Image.Resampling.LANCZOS)
bg = ImageTk.PhotoImage(imgg)
global label
label = Label(root, image=bg)
label.place(x=0, y=0)

root.mainloop()
