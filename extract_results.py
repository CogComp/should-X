#!/usr/bin/env python3

import gcp
from bs4 import BeautifulSoup

version = 11 # increment version to go through pages we are uncertain about again
batch_size = 20

conn, cur = gcp.connect_to_gcp()

print('Connected to DB')

class Result:
    def __init__(self, position, rc):
        self.position = position
        link = rc.find('div', attrs={'class': 'r'}).a
        self.text = link.h3.text
        self.url = link['href']

def remove_divs(doc, div_class):
    for d in doc.find_all('div', attrs={'class': div_class}):
        d.clear()

def do_batch():
    cur.execute('''
        SELECT q.id, html
        FROM queries AS q
          LEFT JOIN search_results AS s ON s.question_id = q.id
        WHERE q.html IS NOT NULL
          AND s.url IS NULL
        FOR UPDATE OF q SKIP LOCKED
        LIMIT %s;''',
        [batch_size])

    for question_id, html in cur.fetchall():
        doc = BeautifulSoup(html, 'html.parser')
        results = []

        try: 
            remove_divs(doc, 'g-blk') # includes suggested queries
            remove_divs(doc, 'kp-wholepage') # knowledge-graph stuff. e.g. 3923397

            for result in doc.find_all('div', attrs={'class': 'rc'}):
                results.append(Result(len(results), result))
                print('    {0}'.format(results[-1].text))
        except Exception as e:
            print('Extraction for {0} failed: {1}'.format(question_id, e))
            continue

        if len(results) > 10:
            print('Too many ({0}) results for query {1}'.format(len(results), question_id))
            continue

        print('Saving results for query {0}'.format(question_id))
        for result in results:
            cur.execute('''
                INSERT INTO search_results (text, url, position, question_id)
                VALUES (%s, %s, %s, %s)
            ''', [result.text, result.url, result.position, question_id])
    conn.commit()
    print('Extracted from {0} pages'.format(batch_size))

while True:
    do_batch()

conn.close()
