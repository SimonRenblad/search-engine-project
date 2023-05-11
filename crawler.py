from urllib.request import urlopen
from bs4 import BeautifulSoup
import requests
import re
import os
import pickle
import json

def fetch_page(url):
    try:
        page = urlopen(url)
    except:
        return None
    soup = BeautifulSoup(page, 'html.parser')
    return soup

def get_links(soup, url):
    links = []
    for link in soup.find_all('a'):
        href = link.get('href')
        links.append(requests.compat.urljoin(url, href))
    return links

def write_page_to_file(url, soup, page_id):
    path = os.path.join("app/index/", str(page_id))
    with open(path, 'w') as f:
        f.write(str(soup))

def fetch_webpages(start_url, num_pages):
    global metadata
    page_id = 1
    queue = [(start_url, 0)]
    visited = set()
    while queue and len(visited) < num_pages:
        url = queue.pop(0)
        if url[0] not in visited:
            soup = fetch_page(url[0])
            if soup:
                write_page_to_file(url[0], soup, page_id)
                links = get_links(soup, url[0])
                for link in links:
                    print(link)
                    queue.append((link,page_id))
                visited.add(url[0])

                # get title, last modified, links
                title = soup.title.string

                # extract the content length
                content_length = len(soup.get_text())

                 # extract the last modified date
                last_modified_tag = soup.find('meta', attrs={'name': 'last-modified'})

                last_modified = "No date"
                if last_modified_tag:
                    last_modified = last_modified_tag['content']

                metadata = json.dumps({'url':url[0], 'parent_id': url[1], 'title': title, 'content-length': content_length, 'last-modified': last_modified, 'links': links[:10]})
                print(metadata)
                output = open(os.path.join('app/metadata/', str(page_id)), "wb")
                pickle.dump(metadata, output, -1)
                output.close()

                page_id += 1
    return visited

if __name__ == "__main__":
    fetch_webpages("https://www.cse.ust.hk/~kwtleung/COMP4321/testpage.htm", 300)