#!/usr/bin/env python3

import gcp
from bs4 import BeautifulSoup

version = 11 # increment version to go through pages we are uncertain about again
batch_size = 20

conn, cur = gcp.connect_to_gcp()

print('Connected to DB')

def get_url(snippet):
    r_div = snippet.find('div', attrs={'class': 'r'})
    if r_div:
        return r_div.a['href']

def do_batch():
    cur.execute('''
        SELECT q.id, html
        FROM queries AS q
          LEFT JOIN extractions AS e ON q.id = e.id
        WHERE q.html IS NOT NULL
          AND e.answer_type = 'feat_snip'
          AND (e.extract_v < %s OR e.extract_v IS NULL)
        FOR UPDATE OF q SKIP LOCKED
        LIMIT %s;''',
        [version, batch_size])

    for id, html in cur.fetchall():
        url = None

        doc = BeautifulSoup(html, 'html.parser')
        featured = doc.h2
        # the casing in the html is inconsistent, so just always lowercase
        featured_type = featured.get_text().lower() if featured else None

        try:
            if featured_type == 'featured snippet from the web':
                snippet = featured.parent.div
                url = get_url(snippet)
            else:
                answered_div = doc.find('div', {'class': 'answered-question'})
                if answered_div:
                    url = get_url(answered_div)
        except Exception as e:
            print('Extraction for {0} failed: {1}'.format(id, e))
            continue

        print('{0:7} {1}'.format(
            id,
            url))
        cur.execute('''
            UPDATE extractions
            SET extract_v = %s, answer_url = %s
            WHERE id = %s;
        ''', [version, url, id])
    conn.commit()
    print('Extracted from {0} pages'.format(batch_size))

while True:
    do_batch()

conn.close()
