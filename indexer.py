import os
import re
from bs4 import BeautifulSoup
from nltk.stem import PorterStemmer
import pickle

# state-ful == global variable
inverted_index = {}
forward_index = {}


def get_stopwords():
    with open(os.path.join("app/stopwords/", 'stopwords.txt')) as f:
        stopwords = set(f.read().split())
    return stopwords

def get_stems(text):
    ps = PorterStemmer()
    words = re.findall(r'\b\w+\b', text.lower())
    stopwords = get_stopwords()
    stems = [ps.stem(word) for word in words if word not in stopwords]
    return stems

def index_page(page_id):
    path = os.path.join("app/index/", str(page_id))
    with open(path, 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    title = soup.title.string if soup.title else ''
    body = soup.get_text()
    title_stems = get_stems(title)
    body_stems = get_stems(body)

    # Generate bigrams and trigrams for body_stems
    body_bigrams = [stem1 + "_" + stem2 for stem1, stem2 in zip(body_stems[:-1], body_stems[1:])]
    body_trigrams = [stem1 + "_" + stem2 + "_" + stem3 for stem1, stem2, stem3 in zip(body_stems[:-2], body_stems[1:-1], body_stems[2:])]

    # Create term frequency map for body_stems and title_stems
    body_tf_map = {}
    title_tf_map = {}
    for stem in body_stems:
        body_tf_map[stem] = body_tf_map.get(stem, 0) + 1
    for stem in title_stems:
        title_tf_map[stem] = title_tf_map.get(stem, 0) + 3 # increase weighting by 3
    for bigram in body_bigrams:
        body_tf_map[bigram] = body_tf_map.get(bigram, 0) + 1 # same weight
    for trigram in body_trigrams:
        body_tf_map[trigram] = body_tf_map.get(trigram, 0) + 1

    # add to forward index
    forward_index[page_id] = body_tf_map

    # Update inverted index with term frequency maps
    for stem, tf in body_tf_map.items():
        if stem not in inverted_index:
            inverted_index[stem] = []
        inverted_index[stem].append((page_id, tf))
    for stem, tf in title_tf_map.items():
        if stem not in inverted_index:
            inverted_index[stem] = []
        inverted_index[stem].append((page_id, tf))

def index_all_pages():
    for filename in os.listdir("app/index/"):
        page_id = int(filename)
        index_page(page_id)

def save_index():
    output = open('app/inverted_index/data.pkl', "wb")
    pickle.dump(inverted_index, output, -1)
    output.close()
    output2 = open('app/forward_index/data.pkl', "wb")
    pickle.dump(forward_index, output2, -1)
    output2.close()
    

if __name__ == "__main__":
    index_all_pages()
    save_index()