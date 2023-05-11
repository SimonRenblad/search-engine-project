from flask import render_template, request
from app import app
from app.retrieval import search

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def do_search():
    query = request.form['query']
    results = search(query)
    return render_template('search.html', query=query, results=results)