import re
from underthesea import word_tokenize
import pandas as pd
from tqdm import tqdm
import glob

def text_preprocessing(doc):
    # remove html tags
    doc = re.sub(r'<[^<>$]*>', '', doc)
    
    # to lower case
    doc = doc.lower()

    # word rokenizing 
    doc = word_tokenize(doc, format='text')

    # remove the wrong characters 
    pattern = r'[^\s\wáàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệóòỏõọôốồổỗộơớờởỡợíìỉĩịúùủũụưứừửữựýỳỷỹỵđ]'
    doc = re.sub(pattern, ' ', doc)

    # replace mutiple space with single space
    doc = re.sub(r'\s+', ' ', doc).strip()

    return doc

def load_data(filepath):
    print('LOAD DATASET')
    df = pd.read_csv(filepath)
    df = df[['name', 'introduction', 'topic']]
    df = df.dropna(thresh=2) # drop row with 2 or more empty cells 

    print('Done \n')
    return df.values # numpy.array

# Load data of all csv files in data folder
def load_all_files_csv(folder_path):
    print('LOAD DATASET')
    files = glob.glob(folder_path + '/*.csv')  # get all files that extension is .csv

    content = []
    for filename in tqdm(files):
        df = pd.read_csv(filename)
        df = df[['name', 'introduction', 'topic']]
        content.append(df)

    data = pd.concat(content)
    data.dropna(thresh=2) # drop row with 2 or more empty cells 
    
    print('Done \n')
    return(data.values)

def extract_inputs_outputs(dataset):
    print('EXTRACT INPUTS AND OUTPUTS')
    inputs = []
    for book in tqdm(dataset[:, :-1]):
        text = f'{book[0]} {book[1]} {book[0]}'
        text = text_preprocessing(text)
        inputs.append(text)

    outputs = list(dataset[:, -1])

    print('Done \n')
    return inputs, outputs

def remove_words(doc, list_words):
    # remove words from the word list in document
    doc_list = doc.split()
    for word in list_words:
        while word in doc_list:
            doc_list.remove(word)
    
    return ' '.join(doc_list)

def get_stopword_and_uniqueword_list(inputs, top, threshold):
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
    stopwords = sorted_count[:top]

    # find unique words
    uniquewords = []
    for word in count:
        if count[word] < threshold:
            uniquewords.append(word)

    # print(f'Top {top} most common words: ')
    # for word in stopwords:
    #     print(f'{word}  ->  {count[word]}')
    # print('-------------------------------')

    # print(f'There are {len(uniquewords)} words that appears less than {threshold} times: ')
    # for word in uniquewords:
    #     print(f'{word}  ->  {count[word]}')
    # print('-------------------------------')

    print('Done \n')
    return stopwords, uniquewords

def dataset_preprocessing(inputs, top, threshold):
    print('PREPROCESS DATA')

    # Get stopwords and uniquewords list
    stopwords, uniquewords = get_stopword_and_uniqueword_list(inputs, top=top, threshold=threshold)

    print('Preprocessing data ...')
    filtered_inputs = []
    for word in tqdm(inputs):
        word = remove_words(word, stopwords)
        word = remove_words(word, uniquewords)
        filtered_inputs.append(word)

    print('Done \n')
    return filtered_inputs
    
def save_preprocessed_data(save_link, filtered_inputs, outputs):
    print('SAVE DATA')

    df = pd.DataFrame({
        'inputs': filtered_inputs,
        'outputs': outputs
    })

    df.to_csv(save_link)
    print('Done \n')

if __name__ == '__main__':
    # declare variable
    data_link = './data/data.csv'
    data_folder = './data'
    save_link = './preprocess_data/preprocessed_data.csv'
    top = 100
    threshold = 2

    # load dataset from csv file
    # dataset = load_data(data_link)
    dataset = load_all_files_csv(data_folder)

    # extract inputs and outputs from dataset
    inputs, outputs = extract_inputs_outputs(dataset)
    
    # filter inputs by remove stop word and unique word
    filtered_inputs = dataset_preprocessing(inputs, top, threshold)

    # save filtered_inputs + outputs to csv file
    save_preprocessed_data(save_link, filtered_inputs, outputs)

    print('Complete preprocessing data \n')
