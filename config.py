import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FORWARD_INDEX_DIR = os.path.join(BASE_DIR, 'forward_index')
INVERTED_INDEX_DIR = os.path.join(BASE_DIR, 'inverted_index')
STOPWORDS_DIR = os.path.join(BASE_DIR, 'stopwords')