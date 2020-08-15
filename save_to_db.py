#!/usr/bin/env python3
# usage: ./save_to_db.py <filename> [start position]

import re
import sys
import psycopg2
import os
import gcp

start = int(sys.argv[2]) if len(sys.argv) >= 3 else 0
line_count = start
processed_count = 0
commit_size = 100

conn, cur = gcp.connect_to_gcp()

def insert_question(question):
    cur.execute('INSERT INTO queries (question) VALUES (%s) ON CONFLICT DO NOTHING;', [question])

with open(sys.argv[1], 'r') as queries:
    # skip first few lines, in case it failed and this is simply continuing from where
    # it left off before
    for line in queries.readlines()[start:]:
        line_count += 1
        line = line.strip()
        # avoid using \w in regex in case Unicode characters get matched too
        #if re.search('^[ a-zA-Z0-9]+$', line):
        insert_question(line)
        processed_count += 1
        
        if processed_count > 0 and processed_count % commit_size == 0:
            conn.commit()
            print('Committed {0} items ending at line {1}'.format(
                commit_size, line_count))
        
conn.commit()
print('Finished at line {0}'.format(line_count))

cur.close()
conn.close()
