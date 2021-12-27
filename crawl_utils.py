import bs4
import requests
import pandas as pd
import os
from tqdm import tqdm 
import time
import re

class VinaBookLinkCrawler:
    def __init__(self, url_format, save_dir):
        self.url_format = url_format
        self.save_dir = save_dir
        if not os.path.exists(self.save_dir):
            os.mkdir(self.save_dir)
        self.label = url_format.split('/')[-2]

    def __call__(self, num_pages):
        self.get_book_links(num_pages=num_pages)

    def get_url(self, page_number):
        return self.url_format % page_number

    def get_page_content(self, page_number):
        url = self.get_url(page_number)
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        assert response.status_code == 200, "Can't connect to this url %s" % url
        return bs4.BeautifulSoup(response.text, 'html.parser')

    def get_book_links(self, num_pages):
        # create file
        save_path = self.save_dir + '/' + self.label + '.txt'
        #if not os.path.exists(save_path):
        for page in tqdm(range(1, num_pages + 1)):
            soup = self.get_page_content(page)

            # crawl book link in this page
            books = soup.find_all('a', class_='image-border')
            with open(save_path, 'a') as f:
                for book in books:
                    f.write(book['href'] + '\n')
        
        print('Done!')
            

class VinaBookContentCrawler:
    def get_page(self, url):
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code != 200:
            print(response.status_code)
        assert response.status_code == 200, "Can't connect to this url"
        return bs4.BeautifulSoup(response.text, 'html.parser')

    def get_content(self, url, label):
        soup = self.get_page(url)
        desc = soup.find('div', class_='full-description')
        book_info = {}

        # label
        book_info['topic'] = label

        # intro
        if desc is None:
            book_info['introduction'] = None
        else:
            contents = desc.find_all('p')
            intro = ''
            for content in contents:
                intro = intro + content.text + '\n'
            intro = intro.strip()
            book_info['introduction'] = intro

        # name
        try:
            name = soup.find('h1', {'itemprop': 'name'}).text.strip()
        except:
            name = None
        book_info['name'] = name

        # price
        price = int(soup.find('span', class_='price-num').text.strip().replace('.', ''))
        book_info['price'] = price

        # cover
        try:
            cover = soup.find('div', class_='bk-cover').find('img')['src']
        except:
            cover = None       
        book_info['cover'] = cover

        # product desc
        detail_box = soup.find('div', {'id': 'product-details-box'})
        if detail_box is None:
            book_info['authors'] = None
            book_info['translator'] = None
            book_info['publisher'] = None
            book_info['printer'] = None
            book_info['id'] = None
            book_info['weight'] = None
            book_info['language'] = None
            book_info['format'] = None
            book_info['width'] = None
            book_info['height'] = None
            book_info['publish_date'] = None
            book_info['pages'] = None
            return book_info

        tags = detail_box.find('div', class_='mainbox2-body').\
                find('div', class_='product-feature').find_all('li')
        
        # set tag
        info_to_tags = {}
        for tag in tags:
            if 'Tác giả' in tag.text:
                info_to_tags['authors'] = tag
            elif 'Người dịch' in tag.text:
                info_to_tags['translator'] = tag
            elif 'Nhà xuất bản' in tag.text:
                info_to_tags['publisher'] = tag
            elif 'Nhà phát hành' in tag.text:
                info_to_tags['printer'] = tag
            elif 'Mã Sản phẩm' in tag.text:
                info_to_tags['id'] = tag
            elif 'Khối lượng' in tag.text:
                info_to_tags['weight'] = tag
            elif 'Ngôn ngữ' in tag.text:
                info_to_tags['language'] = tag
            elif 'Định dạng' in tag.text:
                info_to_tags['format'] = tag
            elif 'Kích thước' in tag.text:
                info_to_tags['size'] = tag
            elif 'Ngày phát hành' in tag.text:
                info_to_tags['publish_date'] = tag
            elif 'Số trang' in tag.text:
                info_to_tags['pages'] = tag

        # arthor
        if 'authors' in info_to_tags:
            arthor_tags = info_to_tags['authors'].find_all('span')
            authors = ''
            for tag in arthor_tags:
                authors += tag.text + ', '
            authors = authors[:-2]
            book_info['authors'] = authors
        else:
            book_info['authors'] = None

        # translator
        if 'translator' in info_to_tags:
            translator = info_to_tags['translator'].find('span', class_='author').text
            book_info['translator'] = translator
        else:
            book_info['translator'] = None

        # publisher
        if 'publisher' in info_to_tags:
            publisher = info_to_tags['publisher'].find('span').text
            book_info['publisher'] = publisher
        else:
            book_info['publisher'] = None

        # printer
        if 'printer' in info_to_tags:
            printer = info_to_tags['printer'].find('a').text
            book_info['printer'] = printer
        else:
            book_info['printer'] = None

        # id
        if 'id' in info_to_tags:
            id = info_to_tags['id'].text.split('\n')[-2].strip()
            book_info['id'] = id
        else:
            book_info['id'] = None

        # weight
        if 'weight' in info_to_tags:
            weight = float(info_to_tags['weight'].text.split('\n')[-2].strip()[:-4].replace(',', '.'))
            book_info['weight'] = weight
        else:
            book_info['weight'] = None

        # language
        if 'language' in info_to_tags:
            language = info_to_tags['language'].text.split('\n')[-1].strip()
            book_info['language'] = language
        else:
            book_info['language'] = None
        
        # format
        if 'format' in info_to_tags:
            format = info_to_tags['format'].text.split('\n')[-1].strip()
            book_info['format'] = format
        else:
            book_info['format'] = None
        
        # size
        if 'size' in info_to_tags:
            size = info_to_tags['size'].text.split('\n')[-1].strip().lower().replace('x', ' ')
            size = re.sub(' +', ' ', size)
            s = size.split(' ')
            width = float(s[0].replace(',', '.').strip())
            try: 
                height = float(s[1].replace(',', '.').strip())
            except:
                height = 0
            book_info['width'] = width
            book_info['height'] = height
        else:
            book_info['width'] = None
            book_info['height'] = None

        # publish date
        if 'publish_date' in info_to_tags:
            publish_date = info_to_tags['publish_date'].find('meta').text.strip()
            book_info['publish_date'] = publish_date
        else:
            book_info['publish_date'] = None

        # number of page
        if 'pages' in info_to_tags:
            pages = int(info_to_tags['pages'].find('span').text)
            book_info['pages'] = pages
        else:
            book_info['pages'] = None

        return book_info

    def get_contents_by_label(self, file):
        label = file.split('/')[-1][:-4]
        
        content_list = []

        with open(file, 'r') as f:
            links = f.read()
            link_list = links.split('\n')
            link_list.pop()
            print('Crawling books from %s ... ' %file)
            for link in tqdm(link_list):
                content = self.get_content(link, label)
                content_list.append(content)
            
            print('Done!')

        return content_list


    def __call__(self, link_dir, file, save_path):
        # files = os.listdir(link_dir)
        # content_list = []
        # for file in files:
        #     content = self.get_contents_by_label(link_dir + '/' + file)
        #     content_list = content_list + content
        
        # df = pd.DataFrame(content_list)
        # df.to_csv(save_path, mode='a')
        link_data = os.getcwd()
        save_path = link_data + "/data/data_" + save_path

        content = self.get_contents_by_label(link_dir + '/' + file)
           
        df = pd.DataFrame(content)
        df.to_csv(save_path, mode='a')
      


if __name__ == '__main__':

    # params
    link_dir = './crawl_links'
    link_dir_data = './data'
    
    # Crawl links
    f = open('link_templates.txt', 'r').read()
    links = f.split('\n')
    
    print('______________________ CRAWL LINKS ______________________')
    print('Starting ...')
    start = time.time()
    for link in links:
        template, pages = link.split(' ')
        link_crawler = VinaBookLinkCrawler(template, link_dir)
        link_crawler.get_book_links(int(pages))

    print('Done !')
    print('Crawling links finish after {:.2f} hours\n'.format((time.time() - start) / 3600))


    # crawl contents
    print('______________________ CRAWL CONTENTS ______________________')
    print('Starting ...')
    start = time.time()
    crawler = VinaBookContentCrawler()

    files = os.listdir(link_dir)
    for file in files:
        data_path = str(file).split(".txt")[0] + ".csv"
        print(data_path)
        crawler(link_dir,file, data_path)
    print('Done !')
    print('Crawling contents finish after {:.2f} hours\n'.format((time.time() - start) / 3600))


    #demo crawl single book
    print('______________________ CRAWL DEMO ______________________')
    print('Starting ...')
    url = "https://www.vinabook.com/bi-quyet-hoi-hoa-ve-tranh-phong-canh-p94187.html"
    data = crawler.get_content(url, label="demo")
    print(data)