import urllib.parse
import requests
import os
import bs4
import urllib3
import certifi
import json
import csv
import re
import time
import random
import re

# Utility functions
XI_SPEECHES = "http://jhsjk.people.cn/result?keywords=&year=209&submit=%E6%90%9C%E7%B4%A2"
MAIN_URL = "http://jhsjk.people.cn/"


def read_url(my_url):
    '''
    Loads html from url. Returns result or "" if the read
    fails.

    Inputs:
        - my_url (str)

    Returns: the html
    '''

    pm = urllib3.PoolManager(
        cert_reqs='CERT_REQUIRED',
        ca_certs=certifi.where())

    return pm.urlopen(url=my_url, method="GET").data


def is_absolute_url(url):
    '''
    Determines if url is an absolute url

    Inputs:
        - url (str)

    Returns: boolean
    '''

    if url == "":
        return False
    return urllib.parse.urlparse(url).netloc != ""


def convert_if_relative_url(new_url, main_url=MAIN_URL):
    '''
    Attempt to determine whether new_url is a relative URL and if so,
    use current_url to determine the path and create a new absolute
    URL.  Will add the protocol, if that is all that is missing.

    Inputs:
        new_url: the path to the restaurants
        main_url: absolute URL

    Returns:
        new absolute URL or None, if cannot determine that
        new_url is a relative URL.

    Examples:
        convert_if_relative_url("/biz/girl-and-the-goat-chicago", "https://www.yelp.com") yields
            'https://www.yelp.com/biz/girl-and-the-goat-chicago'
    '''
    if new_url == "" or not is_absolute_url(main_url):
        return None

    if is_absolute_url(new_url):
        return new_url

    parsed_url = urllib.parse.urlparse(new_url)
    path_parts = parsed_url.path.split("/")

    if len(path_parts) == 0:
        return None

    ext = path_parts[0][-4:]
    if ext in [".edu", ".org", ".com", ".net"]:
        return "http://" + new_url
    else:
        return urllib.parse.urljoin(main_url, new_url)

# find all speeches link


def get_article_link_one_page(search_url):
    '''
    Given the starting link, get all speech urls containing speeches in the year
    2020.

    Returns a list of all urls to be crawled
    '''
    html = read_url(search_url)
    soup = bs4.BeautifulSoup(html, "lxml")
    all_relative_link = [tag['href'] for tag in soup.find_all(
        "a", target="_blank") if tag['href'].startswith('article')]
    good_links = [convert_if_relative_url(link) for link in all_relative_link]

    return good_links


def get_search_page_link(first_link=XI_SPEECHES):
    '''
    From the first page of search requests, get link for second page, third ...
    '''
    html = read_url(first_link)
    soup = bs4.BeautifulSoup(html, "lxml")
    all_search_page_links = {tag['href'] for tag in soup.find_all(
        "a", {'data-ci-pagination-page': True})}

    return all_search_page_links


def get_all_article_links(first_link=XI_SPEECHES):
    '''
    Get all article links (speeches made in 2020).
    '''
    all_article_links = []
    all_search_page_links = list(
        get_search_page_link(first_link)) + [first_link]
    print(all_search_page_links)

    for search_link in all_search_page_links:
        all_article_links += get_article_link_one_page(search_link)

    return all_article_links


def extract_text_date(article_link):
    '''
    Return the date and text_body of from an article link.
    '''

    html = read_url(article_link)
    soup = bs4.BeautifulSoup(html, "lxml")

    # text
    text = soup.find("div", class_="d2txt_con clearfix").text.replace(
        '\n', '').replace('\xa0', '')

    # date
    # attempt 1: locate date within text [last line]
    date_tag = soup.find("div", class_="d2txt_con clearfix").find_all("p")[-1]
    date_processed = re.search(
        "([\d]{4})[\u4e00-\u9fff]+([\d]{2})[\u4e00-\u9fff]+([\d]{2})", date_tag.text)
    if date_processed:
        date = date_processed[1] + "-" + \
            date_processed[2] + "-" + date_processed[3]
    else:
        date_tag = soup.find("div", class_="d2txt_1 clearfix")
        date = re.search("([\d]{4}-[\d]{2}-[\d]{2})", date_tag.text)[0]

    return date, str(text)


def compile_data(first_link=XI_SPEECHES, all_data='all_data.csv'):
    '''
    Returns a csv file with 2 columns, date and text. Each row corresponds to 
    one speech made.
    '''
    with open(all_data, "w") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(['Date', 'Text'])
        for article_link in get_all_article_links(first_link=XI_SPEECHES):
            print(article_link)
            row = extract_text_date(article_link)
            csvwriter.writerow(row)
            print("done with " + article_link)
