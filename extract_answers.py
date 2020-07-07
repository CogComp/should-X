#!/usr/bin/env python3

import gcp
from bs4 import BeautifulSoup

version = 6 # increment version to go through pages we are uncertain about again
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

def get_split(question, delimiter):
    split = question.split(delimiter)
    if len(split) == 2 and len(split[1]) > 0:
        return split[1]

def handle_unit_converter(featured, question):
    equals = featured.parent.div(text='=')[0]
    count = equals.find_next('input')
    count_value = count.get('value')
    unit = count.find_next('option', {'selected': '1'})
    unit_value = ''
    if unit:
        unit_value = unit.get_text()
    else: # see 13783 and 19581
        unit_value = get_split(question, ' how many ')
        if unit_value is None:
            unit_value = get_split(question, ' equal to ')

    short_answer = count_value # sometimes it's just PEBKAC and no units available; see 20802
    if unit_value:
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

def handle_translation_result(featured):
    short_answer = featured.parent.find('pre', {'id': 'tw-target-text'}).get_text()
    return 'tr_result', short_answer, None

def handle_no_snippet(featured):
    return 'no_answer', None, None

def has_no_other_answer_markers(doc):
    return doc.find('div', {'class': 'kp-header'}) is None and \
            doc.find('div', {'class': 'answered-question'}) is None

def do_batch():
    cur.execute('''
        SELECT q.id, question, html
        FROM queries AS q
          LEFT JOIN extractions AS e ON q.id = e.id
        WHERE q.html IS NOT NULL 
          AND e.id = 452538
          AND e.answer IS NULL
          AND e.short_answer IS NULL
          AND e.answer_type IS NULL
          AND (e.extract_v < %s OR e.extract_v IS NULL)
        FOR UPDATE OF q SKIP LOCKED
        LIMIT %s;''',
        [version, batch_size])

    for id, question, html in cur.fetchall():
        extraction_type = None
        short_answer = None
        long_answer = None

        doc = BeautifulSoup(html, 'html.parser')
        featured = doc.h2
        # the casing in the html is inconsistent, so just always lowercase
        featured_type = featured.get_text().lower() if featured else None

        # Examples of ones where featured snippets do not include h2
        # 1389251 
        # 1389246 
        # 1389247 

        # Example of one where it doesn't include 'kp-header' (it does include "answered-question")
        # 41802

        try:
            if featured_type == 'featured snippet from the web':
                extraction_type, short_answer, long_answer = handle_featured_snippet(featured)
            elif featured_type == 'unit converter':
                extraction_type, short_answer, long_answer = handle_unit_converter(featured, question)
            elif featured_type == 'currency converter':
                extraction_type, short_answer, long_answer = handle_currency_converter(featured)
            elif featured_type == 'translation result':
                extraction_type, short_answer, long_answer = handle_translation_result(featured)
            elif has_no_other_answer_markers(doc) and ( \
                featured_type == 'web results' or
                featured_type == 'people also ask' or
                featured_type == 'web result with site links' or
                featured_type is None):
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
