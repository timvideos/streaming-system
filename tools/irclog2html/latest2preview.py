#! /usr/bin/python

import sys
import os

from bs4 import BeautifulSoup

if __name__ == "__main__":
    soup = BeautifulSoup(file(sys.argv[1]).read())

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
    for row in new_order:
        table.append(row)

    table['style'] = "font-size: 8pt;"
    print str(soup)
