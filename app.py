import sys
import tkinter
sys.path.insert(0, "/")

from tkinter import *
from crawl_utils import *
from preprocess_utils import BookIntroPreprocessor, BookDatabaseProcessor
import pickle
import time
import os
import numpy as np

from PIL import Image, ImageTk
import urllib.request
import io
from threading import Thread

path = "saved_model"
curDir = os.path.dirname(os.path.abspath(__file__))
model = pickle.load(open(path + '/best_model.sav', 'rb'))
stopwords = pickle.load(open(path + '/stopwords.sav', 'rb'))
uniquewords = pickle.load(open(path + '/uniquewords.sav', 'rb'))
crawler = VinaBookContentCrawler()
preprocessor = BookIntroPreprocessor().text_preprocessing
text_filter = BookDatabaseProcessor('data/data.csv', 'data/preprocessed_data.csv').remove_words
feature_extractor = pickle.load(open(path + '/feature_extractor.sav', 'rb'))

# Create tkinder window
root = Tk()
root.title('Book Topic Classifier')
root.geometry('900x550')
root.iconbitmap(curDir + '/bookshelf.ico')

# title
name = Label(root, text='Classifier', justify=CENTER, fg='#5f5f5f', bd=2, bg='#f0f0f0')
name.config(font=("Arial", 40))
name.pack(pady=50)

# link input
link_entry = Entry(root, width=50)
link_entry.config(font=('Arial', 14))
link_entry.pack(pady=75, side=TOP)

all_inf0 = {}

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

def get_val(k, my_dict):
    for key, value in my_dict.items():
         if k == key:
             return value

def close_window (window): 
    window.destroy()

def ImgFromUrl(url):
    global image
    with urllib.request.urlopen(url) as connection:
        raw_data = connection.read()
    im = Image.open(io.BytesIO(raw_data))
    image = ImageTk.PhotoImage(im)
    return image

# Process info

def processing():

    inp = link_entry.get()
    if inp == "":
        tkinter.messagebox.showinfo(title='Thông báo', message="Bạn chưa nhập URl\n")
        return 0
    elif "https://www.vinabook.com/" not in inp:
        tkinter.messagebox.showinfo(title='Thông báo', message="URL không hợp lệ\n")
        return 0
    else:
        
        info = ""

        begin = time.time()

        info += f"Crawl dữ liệu từ: {inp}\n"
        start = time.time()
    
        # crawl d? li?u
        infos = crawler.get_content(inp, 'unknown')

        info += 'Crawl time {:.2f}s\n\n'.format(time.time() - start)

        name = infos['name']
        intro = infos['introduction']
        all_inf0.update(infos) 
        
        if name is None or intro is None:
            tkinter.messagebox.showinfo(title='Message', message='\nNot enough information\n')
        else:
            start = time.time()
            data = "{} {} {}".format(name, intro, name)
            data = preprocessor(data)
            data = text_filter(data, stopwords)
            data = text_filter(data, uniquewords)
            
            info += 'Hoàn thành xử lý dữ liệu sau {:.2f} \n\n'.format(time.time() - start)

            # predict
            data = np.array([data])
            feature = feature_extractor.transform(data)
            pred = model.predict(feature)

            info += str(f'=>Kết quả: {get_val(pred[0], name_result)}\n')
            info += '=> Tổng thời gian xử lý:  {:.2f}s\n'.format(time.time() - begin)
            
            newWindow = Toplevel(root)
            newWindow.title("Result")
            newWindow.geometry('1080x350')

            book_result = Label(newWindow, text=info, justify=CENTER, fg='#5f5f5f', bd=2, bg='#f0f0f0')
            book_result.config(font=("Arial", 15))
            book_result.pack(pady=30)
            show_info_btn = Button(newWindow, text='Show Book Infomation', width=20, height=2, font=('Arial', 12, 'bold'), bd=0, bg='crimson', fg='white', command=show_info)
            show_info_btn.pack(side=TOP, pady=20)

def show_info():

    book_info = ""
    book_info += f"Chủ đề: {str(all_inf0['topic'])}\n"
    book_info += f"Tên sách: {str(all_inf0['name'])}\n"
    book_info += f"Giá: {str(all_inf0['price'])} VND\n"
    book_info += f"Giới thiệu: {str(all_inf0['introduction'])} VND\n"
    book_info += f"Tác giả: {str(all_inf0['authors'])}\n"
    book_info += f"Người dịch: {str(all_inf0['translator'])}\n"
    book_info += f"Nhà phát hành: {str(all_inf0['publisher'])}\n"
    book_info += f"Nhà in: {str(all_inf0['printer'])}\n"
    book_info += f"Mã sách: {str(all_inf0['id'])}\n"
    book_info += f"Trọng lượng: {str(all_inf0['weight'])}\n"
    book_info += f"Ngôn ngữ: {str(all_inf0['language'])}\n"
    book_info += f"ĐỊnh dạng: {str(all_inf0['format'])}\n"
    book_info += f"Kích thước: {all_inf0['width']}x{all_inf0['height']}\n"
    book_info += f"Ngày phát hành: {all_inf0['publish_date']}\n"
    book_info += f"Số trang: {all_inf0['pages']}\n"

    infoWindow = Toplevel()
    infoWindow.title("Infomation")
    infoWindow.geometry('1080x1080')


    URL = str(all_inf0['cover'])
    

    result = Text(infoWindow, fg='black', width=114, height=20, bd=1, bg='#f0f0f0')
    result.config(font=("Arial", 9))
    result.pack(pady=10)

    result.insert(END, book_info)

    cover = Label(infoWindow, image=ImgFromUrl(URL))
    cover.config(font=("Arial", 15))
    cover.pack(pady=30)


def startThread():

    thread = Thread(target=processing)

    thread.start()

    return thread
process_btn = Button(root, text='Process', width=16, height=2, font=('Arial', 12, 'bold'), bd=0, bg='crimson', fg='white', command=startThread)
process_btn.pack(side=TOP, pady=20, padx=20)
# Main Loop
root.mainloop()