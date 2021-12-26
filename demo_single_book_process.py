import preprocess_utils as pu
import crawl_utils as cu


print('______________________ CRAWL DEMO ______________________')
print('Starting ...')
url = "https://www.vinabook.com/bi-quyet-hoi-hoa-ve-tranh-phong-canh-p94187.html"
crawler = cu.VinaBookContentCrawler()
data = crawler.get_content(url, label="demo")
print('Done \n')

print('______________________ PREPROCESS DEMO ______________________')
print('Starting ...')
preprocessor =  pu.SingleBookPreprocess(data)
input, output = preprocessor.single_book_preprocessing()

print('input: \n', input)
print('output: \n', output)