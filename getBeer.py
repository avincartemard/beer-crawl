#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" 
Two functions 
getBeerLinks: obtain individual beer URLs from a webpage
getBeerInfo: retrieve beer profile information, store in dictionary
"""

import requests
from bs4 import BeautifulSoup
import numpy as np
import re

def getBeerLinks(pageUrl):
    """ Links to beer descriptions are contained in a list of pages """
    
    # create session with custom HTTP header
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/603.2.5 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.5", 
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
    beerLinks = []
    
    # access url; raise exception is something goes wrong
    try:
        req = session.get(pageUrl, headers=headers)
        req.raise_for_status()
    except Exception:
        print("Error encountered when accessing url; return empty 'beerLinks' list.")
        return beerLinks
    
    # beer urls are all under the h3 header of the blog-list style-1 division 
    try:
        bsObj = BeautifulSoup(req.text, 'lxml')
        beers = bsObj.find({"div"}, {"class": "blog-list style-1"}).findAll("h3")
    except AttributeError:
        print("Attribute error encountered in bsObj; return empty 'beerLinks' list.")
        return beerLinks
    
    # extract individual beer urls
    for beer in beers:
        beerLinks.append(beer.a["href"])
    
    return beerLinks

def getBeerInfo(pageUrl):
    """ Retrieve beer information and store in a Python dictionary """
    
    # create session with custom HTTP header
    session = requests.Session()
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/603.2.5 (KHTML, like Gecko) Version/10.1.1 Safari/603.2.5", 
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
    
    beerInfo = {}
    
    # access url; raise exception is something goes wrong
    try:
        req = session.get(pageUrl, headers=headers)
        req.raise_for_status()
    except Exception:
        print("Error encountered when accessing url; return.")
        return
    
    bsObj = BeautifulSoup(req.text, 'lxml')
    
    # Name and Brewery
    tempName = bsObj.h1.get_text()
    try:
        I = tempName.index('–')
        beerInfo['Name'] = tempName[I+2:]
        beerInfo['Brewery'] = tempName[:I-1]
    except ValueError:
        # if - not in title, may have to parse information manually later
        beerInfo['Name'] = tempName
    
    # Ratings (does not include total)
    for rating in bsObj.findAll("div", {"class": "rate-item"}):
        tempRating = rating.findAll("strong")    # rating and categories within <strong> tag
        beerInfo[tempRating[1].get_text().strip().title()] = np.float64(tempRating[0].get_text())
    # Now treat inconsistencies in ratings systems
    if 'Flavour' in beerInfo:
        beerInfo['Taste'] = beerInfo['Flavour']
    if 'Mouthfeel' in beerInfo:
        beerInfo['Palate'] = beerInfo['Mouthfeel']
        
    # Total score is left empty because some beers are rated with <4 criteria
    # Pandas can handle NaN easily in postprocessing
    
    # Categories found in second panel...
    panel = bsObj.findAll("div", {"class": "panel"})[1]
    
    # Type (located in possibly many <a> tags, so we need to concatenate them)
    beerInfo['Type'] = ", ".join([BeautifulSoup.get_text(type) for type in panel.findAll("li")[0].findAll("a")])
    
    # Pros, Cons, and Conclusion
    panel_list = panel.findAll("li", {"class": "graytext"})
    try:
        beerInfo['Pros'] = panel_list[0].p.get_text()
        beerInfo['Cons'] = panel_list[1].p.get_text()
        beerInfo['Conclusion'] = panel_list[2].p.get_text()
    except IndexError:
        # these categories do not exist
        pass
    
    # Alcohol, Size, and IBU (if available); will need post-processing
    # If value not available, will show up as NaN in .csv file since not in dictionary
    paragraph_row = bsObj.find("div", {"class": "paragraph-row"})
    
    pASI = paragraph_row.parent.findAll("p") # so we can loop through <p> tags
    
    for p in pASI:
        paragraph = p.get_text().title().split()
        if 'Alcohol' in paragraph:
            I = paragraph.index('Alcohol')
            beerInfo['Alcohol'] = paragraph[I+2]
        else:
            continue
        if 'Size' in paragraph:
            I = paragraph.index('Size')
            beerInfo['Size'] = re.sub('\D', '', paragraph[I+2])
        else:
            continue
        if 'Ibu' in paragraph:
            I = paragraph.index('Ibu')
            beerInfo['IBU'] = paragraph[I+2]
        else:
            continue
            
    
#    pASI = overview_header.findNext("p").findNext("p")    # usual position of these features
#    if len(pASI.get_text()) < 2:
#        # if "empty" paragraph (i.e. one unicode character), then use next paragraph
#        pASI = pASI.findNext("p")
#     
#    try:
#        pASI.a.extract()    # eliminate <a> tags, if present, because irrelevant
#    except AttributeError:
#        pass
#    
#    for br in pASI.findAll("br"):
#        try:    # some pages have HTML formatting like <b> that makes it harder to extract
#            br_sib = br.previous_sibling    # actual element we are interested in
#            I = br_sib.index('–')
#            beerInfo[br_sib[:I-1].strip()] = br_sib[I+2:]
#            br_sib = br.next_sibling 
#        except Exception:
#            pass
#    # the last br_sib does not always exist; verify with try statement
#    try:
#        I = br_sib.index('–')
#        beerInfo[br_sib[:I-1].strip()] = br_sib[I+2:]
#    except Exception:
#        pass
    
    # Date reviewed
    beerInfo['Date Reviewed'] = bsObj.find("span", {"class", "dtreviewed"}).span["title"]
    
    # Reviewer (take last element of the title attribute "Posts by *reviewer*")
    beerInfo['Reviewer'] = bsObj.find("span", {"class", "reviewer"}).a["title"].split().pop()
    
    # Categories and Tags
    articleFoot = bsObj.find("div", {"class": "article-foot"})
    
    categoryLinks = articleFoot.find("div", {"class": "left"}).findAll("a")
    categoryList = []
    for category in categoryLinks:
        categoryList.append(category.get_text())
    beerInfo['Categories'] = ", ".join(categoryList)
    
    tagLinks = articleFoot.find("div", {"class": "right"}).findAll("a")
    tagList = []
    for tag in tagLinks:
        tagList.append(tag.get_text())
    beerInfo['Tags'] = ", ".join(tagList)
    
    # Review text and URL
    overview_header = bsObj.find("div", {"class": "paragraph-row"}).findNext("h2").findNext("h2")
    beerInfo['Review Text'] = overview_header.findNext("p").get_text()
    beerInfo['URL'] = pageUrl    # for identification of duplicates
    
    return beerInfo