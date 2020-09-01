#!/usr/bin/env python3

import gcp
import json

conn, cur = gcp.connect_to_gcp()

def get_next_results(start):
    cur.execute('''
        SELECT q.id, q.question, e.short_answer, e.answer, e.answer_type
        FROM queries AS q
        LEFT JOIN extractions AS e ON q.id = e.id
        WHERE q.html IS NOT NULL
          AND q.id >= %s AND q.id < %s
        ORDER BY q.id ASC;
    ''', [start, start + 10000])
    for row in cur.fetchall():
        (id, question, short_answer, answer, answer_type) = row 
        yield {
            'id': id,
            'question': question,
            'short_answer': short_answer,
            'answer': answer,
            'answer_type': answer_type
        }

max_id = 0

with open('dump.json', 'w') as dump:
    has_results = True
    while has_results:
        has_results = False
        for json_result in get_next_results(max_id + 1): # +1 so that we skip the last ID we grabbed
            json.dump(json_result, dump)
            dump.write('\n')
            has_results = True
            max_id = max(max_id, json_result['id'])
        print('Dumped up to question {0}'.format(max_id))

conn.close()
