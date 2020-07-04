#!/usr/bin/env python3

import gcp
from bs4 import BeautifulSoup

version = 1 # increment version to go through pages we are uncertain about again
batch_size = 20

conn, cur = gcp.connect_to_gcp()

print('Connected to DB')

# 详细内容
# 反馈
# 关于精选摘要

class HtmlHandler:
    def __init__(self, doc):
        self.doc = doc

class FeaturedSnippetHandler(HtmlHandler):
    def can_handle(self):
        self.featured = self.doc.find('h2', text='Featured snippet from the web')
        return self.featured is not None

    def handle(self):
        snippet = self.featured.parent.div
        short_answer_div = snippet.find('div', attrs={'data-tts': 'answers'})
        short_answer = None
        if short_answer_div:
            short_answer = short_answer_div.get_text()
            short_answer_div.parent.decompose() # make it easier to find long answer
        long_div = snippet.find('div', attrs={'role': 'heading'})
        if long_div and long_div.span:
            long_answer = long_div.span.get_text()
            return 'feat_snip', short_answer, long_answer
        else:
            return 'rich_snip', short_answer, None

handlers = [FeaturedSnippetHandler]

def do_batch():
    cur.execute('''
        SELECT q.id, html
        FROM queries AS q
          LEFT JOIN extractions AS e ON q.id = e.id
        WHERE q.html IS NOT NULL 
          AND e.answer IS NULL
          AND e.short_answer IS NULL
          AND e.answer_type IS NULL
          AND (e.extract_v < %s OR e.extract_v IS NULL)
        LIMIT %s;''',
        [version, batch_size])

    for id, html in cur.fetchall():
        doc = BeautifulSoup(html, 'html.parser')
        extraction_type = None
        short_answer = None
        long_answer = None
        failed = False

        for potential_handler in handlers:
            handler = potential_handler(doc)
            if handler.can_handle():
                try:
                    extraction_type, short_answer, long_answer = handler.handle()
                except Exception as e:
                    print('Extraction for {0} failed: {1}'.format(id, e))
                    failed = True
                break
        if failed:
            continue

        long_str = long_answer
        if long_str and len(long_str) > 50:
            long_str = long_str[:24] + '...' + long_str[-23:]
        print('#{0}. Extraction: {1}. Short ans: {2}. Long ans: {3}'.format(
            id,
            extraction_type,
            short_answer,
            long_str))
        cur.execute('''
            INSERT INTO extractions (id, short_answer, answer, answer_type, extract_v)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id)
            DO UPDATE
              SET
                short_answer = EXCLUDED.short_answer,
                answer = EXCLUDED.answer,
                answer_type = EXCLUDED.answer_type,
                extract_v = EXCLUDED.extract_v;
        ''', [id, short_answer, long_answer, extraction_type, version])
    conn.commit()
    print('Extracted from {0} pages'.format(batch_size))

while True:
    do_batch()

conn.close()
