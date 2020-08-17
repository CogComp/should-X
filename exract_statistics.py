#!/usr/bin/env python3

import gcp
from bs4 import BeautifulSoup


# psql -h 35.224.30.107 -p 5432 postgres postgres
#
# postgres=> \dt
#             List of relations
#  Schema |    Name     | Type  |  Owner
# --------+-------------+-------+----------
#  public | extractions | table | postgres
#  public | progress    | table | postgres
#  public | queries     | table | postgres
#
#
# postgres=> select answer_type, count(*) from extractions group by 1 order by 2 desc;
#  answer_type |  count
# -------------+---------
#  feat_snip   | 2346122
#  no_answer   | 1244358
#  rich_list   |  144855
#  rich_snip   |  136105
#  rich_set    |  132928
#              |   70344
#  unit_conv   |   43265
#  local_rst   |   25798
#  knowledge   |   22361
#  descript    |   18715
#  tr_result   |   13765
#  curr_conv   |    9509
#  time_conv   |    2395
#  direction   |    1948
#  localtime   |    1463
#  weather     |     656
# (16 rows)
#
#
# # Replace "curr_conv"
# select id from extractions where answer_type = 'curr_conv' limit 10;
#
# # time_conv
#
# http://167.172.127.1/questions?id=3437107
#
#
# # currency conv
# http://167.172.127.1/questions?id=10664
#
#
# # knowledge
# http://167.172.127.1/questions?id=3471342
#
# # overview with long ans
# http://167.172.127.1/questions?id=3916071
# http://167.172.127.1/questions?id=1049060
#


version = 10 # increment version to go through pages we are uncertain about again
batch_size = 20

conn, cur = gcp.connect_to_gcp()

print('Connected to DB')

def count_total_html_extracted():
    cur.execute('''
        SELECT count(*)
        FROM queries AS q
          LEFT JOIN extractions AS e ON q.id = e.id
        WHERE q.html IS NOT NULL
        LIMIT %s;''',
        [batch_size])

    print(cur.fetchall())



def count_total_answer_extracted():
    cur.execute('''
        SELECT q.id, question, html
        FROM queries AS q
          LEFT JOIN extractions AS e ON q.id = e.id
        WHERE e.answer IS NOT NULL 
          OR e.short_answer IS NOT NULL
        FOR UPDATE OF q SKIP LOCKED
        LIMIT %s;''',
        [version, batch_size])


count_total_html_extracted()