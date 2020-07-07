#!/usr/bin/env python3

import gcp
from bs4 import BeautifulSoup

version = 4 # increment version to go through pages we are uncertain about again
batch_size = 20

conn, cur = gcp.connect_to_gcp()

print('Connected to DB')

# 详细内容
# 反馈
# 关于精选摘要

def handle_featured_snippet(featured):
    snippet = featured.parent.div
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

def handle_unit_converter(featured):
    equals = featured.parent.div(text='=')[0]
    count = equals.find_next('input')
    count_value = count.get('value')
    unit = count.find_next('option', {'selected': '1'})
    unit_value = unit.get_text()
    short_answer = '{0} {1}'.format(count_value, unit_value)
    return 'unit_conv', short_answer, None

def handle_currency_converter(featured):
    input = featured.parent.find('select')
    count = input.find_next('input')
    count_value = count.get('value')
    unit = count.find_next('option', {'selected': '1'})
    unit_value = unit.get_text()
    short_answer = '{0} {1}'.format(count_value, unit_value)
    return 'curr_conv', short_answer, None

def handle_no_snippet(featured):
    return 'no_answer', None, None

def has_no_other_answer_markers(doc):
    return doc.find('div', {'class': 'kp-header'}) is None and \
            doc.find('div', {'class': 'answered-question'}) is None

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
        FOR UPDATE OF q SKIP LOCKED
        LIMIT %s;''',
        [version, batch_size])

    for id, html in cur.fetchall():
        extraction_type = None
        short_answer = None
        long_answer = None

        doc = BeautifulSoup(html, 'html.parser')
        featured = doc.h2
        featured_type = featured.get_text() if featured else None

        # Examples of ones where featured snippets do not include h2
        # 1389251 
        # 1389246 
        # 1389247 

        # Example of one where it doesn't include 'kp-header' (it does include "answered-question")
        # 41802

        try:
            if featured_type == 'Featured snippet from the web':
                extraction_type, short_answer, long_answer = handle_featured_snippet(featured)
            elif featured_type == 'Unit Converter':
                extraction_type, short_answer, long_answer = handle_unit_converter(featured)
            elif featured_type == 'Currency Converter':
                extraction_type, short_answer, long_answer = handle_currency_converter(featured)
            elif featured_type == 'People also ask' and has_no_other_answer_markers(doc):
                # featured answers come before this, so if we see this as the first h2, that means
                # there were no featured answers
                extraction_type, short_answer, long_answer = handle_no_snippet(featured)
            elif featured_type == 'Web results' and has_no_other_answer_markers(doc):
                extraction_type, short_answer, long_answer = handle_no_snippet(featured)
            elif featured_type is None and has_no_other_answer_markers(doc):
                # featured answers always start with an h2
                extraction_type, short_answer, long_answer = handle_no_snippet(featured)
            else:
                print('        Unknown featured display "{0}"'.format(featured_type))
        except Exception as e:
            print('Extraction for {0} failed: {1}'.format(id, e))
            continue

        long_str = long_answer
        if long_str and len(long_str) > 50:
            long_str = long_str[:24] + '...' + long_str[-23:]
        print('{0:7} {1:10} Short ans: {2}. Long ans: {3}'.format(
            id,
            str(extraction_type),
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
