#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to obtain beer URLs and retrieve/store information.
"""

import time
import csv
import re

# import two functions to perform webcrawling
from getBeer import getBeerLinks, getBeerInfo

searchForNewBeers = False
# First store all beer review URLs in a .txt file
# while making sure there are no duplicates

if searchForNewBeers:
    # open or create file (if non-existant)
    try:
        f = open('beerURLs.txt', 'r+')
    except FileNotFoundError:
        f = open('beerURLs.txt', 'w+')
        
    beerUrlList = f.read().strip().split('\n')    # list from text file
    newBeerLinks = []   # list to store new beer review URLs
    
    # retrieving beer review URLs from all 35 pages
    for pageNum in range(1, 36):
        pageUrl = 'http://beermebc.com/category/bestbeers/page/' + str(pageNum) + '/'
        beerLinks = getBeerLinks(pageUrl)    # beer links on specific page
        for link in beerLinks:
            if link not in beerUrlList:    # avoid duplicates
                newBeerLinks.append(link)
        time.sleep(3)    # crawling courtesy (total time ~ 1m45s)
    
    f.write('\n'.join(newBeerLinks) + '\n')
    f.close()

# Second, retrieve and store information for all beer reviews

# create list of beer URLs
f = open('beerURLs.txt', 'r')
beerUrlList = f.read().strip().split('\n')    # beer URL list from text file

# initialize .csv dataframe (data stored in dictionary)
beerKeys = ['Name', 'Appearance', 'Aroma', 'Taste', 'Palate', 'Total',
'Type', 'Brewery', 'Pros', 'Cons', 'Conclusion', 'Alcohol', 'IBU', 'Size',
'Date Reviewed', 'Reviewer', 'Categories', 'Tags', 'Review Text', 'URL']
csvFile = open('beer_info.csv', 'w+')
writer = csv.DictWriter(csvFile, beerKeys, extrasaction='ignore')
writer.writeheader()

# create .csv file with beer information
for pageUrl in beerUrlList:
    print(pageUrl)
    try:
        time.sleep(5)    # crawling courtesy (total time ~ 30mins)
        beerInfo = getBeerInfo(pageUrl)
    except Exception:
        print('Exception encountered while executing getBeerInfo()')
        continue
    try:
        # get rid of all the non-ascii-encodable characters in beerInfo
        for key in beerInfo.keys():
            if isinstance(beerInfo[key], str):
                beerInfo[key] = re.sub(r'[^\x00-\x7f]', r' ', beerInfo[key])
        writer.writerow(beerInfo);
    except UnicodeDecodeError:
        print('UnicodeDecodeError encountered - beerInfo not written to .csv file')
        continue

csvFile.close()