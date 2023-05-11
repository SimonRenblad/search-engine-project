import math
import os
import re
import pickle
from bs4 import BeautifulSoup
from app import app
import json
from nltk.stem import PorterStemmer

inverted_index = {}
forward_index = {}

def get_stopwords():
    with open("app/stopwords/stopwords.txt") as f:
        stopwords = set(f.read().split())
    return stopwords

def get_stems(text):
    ps = PorterStemmer()
    words = re.findall(r'\b\w+\b', text.lower())
    stopwords = get_stopwords()
    stems = [ps.stem(word) for word in words if word not in stopwords]
    return stems


def get_idf(stem):
    nt = len(inverted_index.get(stem, []))
    N = len(forward_index.keys())
    return math.log10(N/nt) if nt > 0 else 0

def get_tf(stem, page_id):
    return forward_index[page_id][stem]

def get_term_weight(stem, page_id):
    tf = get_tf(stem, page_id)
    idf = get_idf(stem)
    max_tf = max(forward_index[page_id].values())
    return tf*idf/max_tf if max_tf > 0 else 0

def cosine_similarity(v1, v2):
    dot_product = sum(v1.get(stem, 0)*v2.get(stem, 0) for stem in set(v1.keys()) & set(v2.keys()))
    magnitude_v1 = math.sqrt(sum(v1.get(stem, 0)**2 for stem in v1))
    magnitude_v2 = math.sqrt(sum(v2.get(stem, 0)**2 for stem in v2))
    return dot_product/(magnitude_v1*magnitude_v2) if magnitude_v1*magnitude_v2 > 0 else 0

def get_query_vector(query):
    query_stems = get_stems(query)
    vector = {}
    for stem in query_stems:
        vector[stem] = get_idf(stem)
    return vector

def load_inverted_index():
    global inverted_index
    pkl_file = open("app/inverted_index/data.pkl", 'rb')
    inverted_index = pickle.load(pkl_file)
    pkl_file.close()

def load_forward_index():
    global forward_index
    pkl_file = open("app/forward_index/data.pkl", 'rb')
    forward_index = pickle.load(pkl_file)
    pkl_file.close()

def get_document_info(docId, score):
    pkl_file = open(os.path.join("app/metadata/", str(docId)), "rb")
    metadata = json.loads(pickle.load(pkl_file))
    pkl_file.close()
    termFreq = forward_index[docId]
    metadata["term-frequencies"] = sorted(termFreq.items(), key=lambda x: -x[1])[:5]
    metadata["score"] = score
    return metadata

def search(query):
    load_inverted_index()
    load_forward_index()
    query_vector = get_query_vector(query)
    scores = {}
    for page_id, document_vector in forward_index.items():
        score = cosine_similarity(query_vector, document_vector)
        if score > 0:
            scores[page_id] = score

    # document_ids in order
    ranked_pages = sorted(scores.items(), key=lambda x: -x[1])

    return_pages = [get_document_info(docId, score) for (docId,score) in ranked_pages]
    
    return return_pages[:50] if len(return_pages) > 0 else []
