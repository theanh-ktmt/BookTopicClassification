import re
from underthesea import word_tokenize
import pandas as pd
from tqdm import tqdm
import glob
import pickle

def text_preprocessing(doc):
    # remove html tags
    doc = re.sub(r'<[^<]*>', '', doc)
    
    # to lower case
    doc = doc.lower()

    # word rokenizing 
    doc = word_tokenize(doc, format='text')

    # bo nhung ky tu sai
    pattern = r'[^\s\wáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệóòỏõọôốồổỗộơớờởỡợíìỉĩịúùủũụưứừửữựýỳỷỹỵđ]'
    doc = re.sub(pattern, ' ', doc)

    # replace mutiple space with single space
    doc = re.sub(r'\s+', ' ', doc).strip()

    # replace mutiple line breaks with single space
    doc = re.sub(r'\n+', ' ', doc)

    return doc

# def load_data(filepath):
#     print('LOAD DATASET')
#     df = pd.read_csv(filepath)
#     df = df[['name', 'introduction', 'topic']]
#     df = df.dropna(thresh=2) # Loại bỏ dòng nếu có ô trống, giữu lại những dòng có ít nhất 2 ô dữ liệu

#     print('Done \n')
#     return df.values # numpy.array

class BookDatabaseProcessor:
    def __init__(self, folder_path, save_path, top=100, threshold=2):
        self.folder_path = folder_path
        self.save_path = save_path
        self.top = top
        self.threshold = threshold
        self.dataset = None

    # Load data of all csv files in data folder
    def load_all_files_csv(self):
        print('LOAD DATASET')
        files = glob.glob(self.folder_path + '/*.csv')  # get all files that extension is .csv

        content = []
        for filename in tqdm(files):
            try: 
                df = pd.read_csv(filename)
                df = df[['name', 'introduction', 'topic']]
                content.append(df)
            except:
                continue

        data = pd.concat(content)
        data = data.dropna() # Loại bỏ dòng nếu có ô trống, giữu lại những dòng có ít nhất 2 ô dữ liệu
        
        print('Done \n')
        return(data.values)

    def extract_inputs_outputs(self, dataset):
        print('EXTRACT INPUTS AND OUTPUTS')
        inputs = []
        for book in tqdm(dataset[:, :-1]):
            try:
                text = f'{book[0]} {book[1]} {book[0]}'
                text = text_preprocessing(text)
                inputs.append(text)
            except:
                continue

        outputs = list(dataset[:, -1])

        print('Done \n')
        return inputs, outputs

    def remove_words(self, doc, list_words):
        # remove words in word list
        words = doc.split(' ')
        res = list()
        for word in words:
            if word not in list_words:
                res.append(word)
        
        return ' '.join(res)

    def get_stopword_and_uniqueword_list(self, inputs):
        print('Counting words ... ')
        # count the number of each word in input word list
        count = {}
        for content in tqdm(inputs):
            words = content.split(' ')
            for word in words:
                if word not in count:
                    count[word] = 1
                else:
                    count[word] += 1

        print(f'Number of words in dataset: {len(count)} \n')

        print('Get stopwords and uniquewords list ...')

        # sort list word by decreasing value
        sorted_count = sorted(count, key=count.get, reverse=True)

        # find stopwords
        stopwords = sorted_count[:self.top]

        # find unique words
        uniquewords = []
        for word in count:
            if count[word] < self.threshold:
                uniquewords.append(word)
        
        print('Done \n')
        return stopwords, uniquewords


    def save_preprocessed_data(self, inputs, outputs):
        print('SAVE DATA')

        df = pd.DataFrame({
            'inputs': inputs,
            'outputs': outputs
        })

        df.to_csv(save_link)
        print('Done \n')


    def dataset_preprocessing(self):
        print('______________________ PREPROCESS DATA ______________________')
        print('Starting ...')

        # load dataset from csv file
        self.dataset = self.load_all_files_csv()

        # extract inputs and outputs from dataset
        inputs, outputs = self.extract_inputs_outputs(self.dataset)

        # get stop word and unique word 
        stopwords, uniquewords = self.get_stopword_and_uniqueword_list(inputs)

        # save stopwords and uniquewords
        pickle.dump(stopwords, open('./saved_model/stopwords.sav', 'wb'))
        pickle.dump(uniquewords, open('./saved_model/uniquewords.sav', 'wb'))
    
        # preprocess inputs, filter inputs by remove stop word and unique word
        print('Preprocessing data ...')
        filtered_inputs = []
        for word in tqdm(inputs):
            word = self.remove_words(word, stopwords)
            word = self.remove_words(word, uniquewords)
            filtered_inputs.append(word)

        print('Done \n')

        # Save filtered_inputs + outputs to csv file
        self.save_preprocessed_data(filtered_inputs, outputs)
        

class SingleBookPreprocess():

    def __init__(self, stopwords, uniquewords):
        self.stopwords = stopwords
        self.uniquewords = uniquewords

    def remove_words(self, doc, list_words):
        # remove words in word list
        words = doc.split(' ')
        res = list()
        for word in words:
            if word not in list_words:
                res.append(word)
        
        return ' '.join(res)

    def single_book_preprocessing(self, book_data):
        name = book_data['name']
        introduction = book_data['introduction']
        topic = book_data['topic']

        input = f'{name} {introduction} {name}'

        # preprocess
        input = text_preprocessing(input)
        input = self.remove_words(input, self.stopwords)
        input = self.remove_words(input, self.uniquewords)

        return input, topic

if __name__ == '__main__':
    # declare variable
    data_folder = './data'
    save_link = './preprocessed_data/preprocessed_data.csv'
    top = 100
    threshold = 2

    bookprocessor = BookDatabaseProcessor(data_folder, save_link, top, threshold)
    bookprocessor.dataset_preprocessing()

    print('Complete preprocessing data \n')
