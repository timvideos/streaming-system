#! /usr/bin/python

import sys
import os
import re

import slimmer
from bs4 import BeautifulSoup

if __name__ == "__main__":
    soup = BeautifulSoup(file(sys.argv[1]).read())

    # Remove tags we don't need
    for meta in soup.find_all("meta"):
        meta.extract() 
    for title in soup.find_all("title"):
        title.extract() 

    # Remove attributes we don't need
    for a in soup.find_all("a"):
        if a['href'].startswith('#'):
            del a['href']
    for tr in soup.find_all("tr"):
        del tr['id']

    # Make attributes shorter
    for tag in soup.find_all(re.compile(".*")):
        try:
            tag['class'] = tag['class'][0]
        except KeyError:
            pass

    body = soup.find("body")
    body['style'] = "background: transparent;"

    # Remove the unwanted decoration.
    [x.decompose() for x in soup.find_all("div", {"class": "navigation"})]
    [x.decompose() for x in soup.find_all("div", {"class": "generatedby"})]
    [x.decompose() for x in soup.find_all("h1")]
    [x.decompose() for x in soup.find_all("div", {"class": "searchbox"})]

    # Reverse the table rows.
    table = soup.find("table")
    new_order = []
    for row in list(table.children):
        new_order.insert(0, row.extract())
    for row in new_order[:40]:
        table.append(row)

    table['style'] = "font-size: 8pt;"
#    print str(soup)
    print slimmer.xhtml_slimmer(str(soup))
