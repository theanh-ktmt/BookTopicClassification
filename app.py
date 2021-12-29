import sys
import tkinter
from tkinter import font
sys.path.insert(0, "./")

from tkinter import *
from crawl_utils import VinaBookContentCrawler
from preprocess_utils import SingleBookPreprocess
from PIL import Image, ImageTk
import urllib.request
from threading import Thread
import numpy as np
import pickle
import time
import os
import io

# var
path = "saved_model"
curDir = os.path.dirname(os.path.abspath(__file__))
BG_COLOR = "azure"
TEXT_COLOR = "gray"
BUTTON_COLOR = "dodgerblue"

# chuyển nhãn sang tiếng việt
name_result = {
    'am-nhac-1': 'Âm nhạc',
    'chinh-tri-triet-hoc': 'Chính trị triết học',
    'du-lich-1': 'Du lịch',
    'khoa-hoc-co-ban': 'Khoa học cơ bản',
    'khoa-hoc-ky-thuat': 'Khoa học kỹ thuật',
    'khoa-hoc-tu-nhien-xa-hoi': 'Khoa học xã hội',
    'lich-su-dia-ly': 'Lịch sử, địa lý',
    'my-thuat-kien-truc':'Mỹ thuật kiến trúc',
    'nghiep-vu-bao-chi': 'Nghiệp vụ báo chí',
    'nong-lam-nghiep': 'Nông lâm nghiệp',
    'phap-luat-1': 'Pháp luật',
    'sach-hoc-nghe': 'Sách học nghề',
    'sach-ton-giao': 'Sách tôn giáo',
    'van-hoa-nghe-thuat': 'Văn hóa nghệ thuật',
    'y-hoc': 'Y học'
}

# load model
model = pickle.load(open(path + '/best_model.sav', 'rb'))

# load stopwords và uniquewords
stopwords = pickle.load(open(path + '/stopwords.sav', 'rb'))
uniquewords = pickle.load(open(path + '/uniquewords.sav', 'rb'))

# tạo crawler và preprocessor
crawler = VinaBookContentCrawler()
preprocessor = SingleBookPreprocess(stopwords, uniquewords)

# load feature extractor
feature_extractor = pickle.load(open(path + '/feature_extractor.sav', 'rb'))

# Create main window
root = Tk()
root.title('Book Topic Classifier')
root.geometry('900x360')
root.iconbitmap(curDir + '/bookshelf.ico')
root.config(bg=BG_COLOR)

# title
name = Label(root, text='Book Topic Classification', justify=CENTER, fg=TEXT_COLOR, bd=2, bg=BG_COLOR)
name.config(font=("Arial", 24))
name.pack(side=TOP, pady=50)

# link input
link_entry = Entry(root, width=60, justify=CENTER, fg=BUTTON_COLOR)
link_entry.config(font=('Arial', 14))
link_entry.pack(side=TOP, pady=10)

all_inf0 = {}

def ImgFromUrl(url):
    global image
    with urllib.request.urlopen(url) as connection:
        raw_data = connection.read()
    im = Image.open(io.BytesIO(raw_data)).resize((200, 280))
    image = ImageTk.PhotoImage(im)
    return image

# Process info
def processing():
    inp = link_entry.get()

    # không nhập input
    if inp == "":
        tkinter.messagebox.showinfo(title='Alert', message="URL is empty!\n")
        return

    # Nhập sai đường dẫn
    elif "https://www.vinabook.com/" not in inp:
        tkinter.messagebox.showinfo(title='Alert', message="Invalid URL!\n")
        return

    # Nhập đúng
    else:
        begin = time.time()

        # crawl dữ liệu
        infos = crawler.get_content(inp, 'demo')
        crawl_time = time.time() - begin

        name = infos['name']
        intro = infos['introduction']
        all_inf0.update(infos) 
        
        # Sách không có tên hoặc không có intro
        if name is None or intro is None:
            tkinter.messagebox.showinfo(title='Alert', message='Not enough information\n')

        # Hợp lệ
        else:
            # tiền xử lý
            start = time.time()
            data, _ = preprocessor.single_book_preprocessing(infos)
            process_time = time.time() - start

            # dự đoán
            data = np.array([data])
            feature = feature_extractor.transform(data)
            pred = model.predict(feature)
            result = name_result[pred[0]]
            total_time = crawl_time + process_time
            
            # mở cửa số thông tin
            newWindow = Toplevel(root)
            newWindow.title("Result")
            newWindow.geometry('600x360')
            newWindow.iconbitmap(curDir + '/bookshelf.ico')
            newWindow.config(bg=BG_COLOR)
            
            FONT1 = ('Aria', 12)
            FONT2 = ('Aria', 16, 'bold')

            pad_label1 = Label(newWindow, bg=BG_COLOR)
            pad_label1.pack(side=TOP, pady=5)

            res_label = Label(newWindow, text='Result', font=FONT1, bg=BG_COLOR, fg='gray')
            res_label.pack(side=TOP, pady=5)

            res_dis = Label(newWindow, text=result, font=FONT2, bg=BG_COLOR, fg=BUTTON_COLOR)
            res_dis.pack(side=TOP)

            pad_label2 = Label(newWindow, bg=BG_COLOR)
            pad_label2.pack(side=TOP, pady=10)

            time_label = Label(newWindow, text='Total = Crawl + Preprocess', font=FONT1, bg=BG_COLOR, fg='gray')
            time_label.pack(side=TOP, pady=5)

            time_dis = Label(newWindow, text="{:.2f}s = {:.2f}s + {:.2f}s".format(total_time, crawl_time, process_time), font=FONT2, bg=BG_COLOR, fg=BUTTON_COLOR)
            time_dis.pack(side=TOP)

            show_info_btn = Button(newWindow, text='Show Book Infomation', width=24, height=2, font=('Arial', 12, 'bold'), bd=0, bg=BUTTON_COLOR, fg='white', command=show_info)
            show_info_btn.pack(side=BOTTOM, pady=30)

def show_info():
    infoWindow = Toplevel()
    infoWindow.title("Book Infomation")
    infoWindow.geometry('900x620')
    infoWindow.iconbitmap(curDir + '/bookshelf.ico')
    infoWindow.config(bg=BG_COLOR)

    S_FONT = ('Arial', 9)
    B_FONT = ('Arial', 9, 'bold')

    URL = str(all_inf0['cover'])
    n = 4
    pad_size = 3
    width = 28

    # cover
    lf = LabelFrame(infoWindow, text=all_inf0['name'], bg=BG_COLOR, fg='gray', font=B_FONT)
    lf.grid(row=0, column=0, pady=4, columnspan=n)

    content = Label(lf, image=ImgFromUrl(URL), bg=BG_COLOR)
    content.pack(padx=2, pady=2)

    # Hiển thị thông tin
    info_list = ['id', 'authors', 'price', "translator", 'publisher', 'printer', 'weight', 'language', 'format', 'size', 'publish_date', 'pages']
    for i, key in enumerate(info_list):
        if key == 'size':
            lf = LabelFrame(infoWindow, text=key.title(), bg=BG_COLOR, fg='gray', font=B_FONT)
            lf.grid(row=i//n + 1, column=i%n, pady=pad_size, padx=pad_size)

            content = Label(lf, text="{}x{} cm".format(all_inf0['width'], all_inf0['height']), font=S_FONT, bg=BG_COLOR, fg='gray', width=width)
            content.pack(padx=2, pady=2)
        else:
            lf = LabelFrame(infoWindow, text=key.title(), bg=BG_COLOR, fg='gray', font=B_FONT)
            lf.grid(row=i//n + 1, column=i%n, pady=pad_size, padx=pad_size)

            content = Label(lf, text=all_inf0[key], font=S_FONT, bg=BG_COLOR, fg='gray', width=width)
            content.pack(padx=2, pady=2)

    lf = LabelFrame(infoWindow, text='Introduction', bg=BG_COLOR, fg='gray', font=B_FONT, bd=0)
    lf.grid(row=4, column=0, columnspan=n, pady=pad_size, padx=pad_size)

    content = Text(lf, width=126, height=8, font=S_FONT, bg=BG_COLOR, fg='gray', bd=0)
    content.insert(END, all_inf0['introduction'])
    content.pack(padx=2, pady=2)

def startThread():
    thread = Thread(target=processing)
    thread.start()
    return thread
    
process_btn = Button(root, text='Process', width=16, height=2, font=('Arial', 12, 'bold'), bd=0, bg=BUTTON_COLOR, fg='white', command=startThread)
process_btn.pack(side=TOP, pady=20, padx=20)

# Main Loop
root.mainloop()