#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import psycopg2
import os
import time
import random

chrome_options = Options()
chrome_options.add_argument("--window-size=1024x768")
# chrome_options.add_argument("--headless")
chrome_options.add_argument('log-level=3')
driver = webdriver.Chrome(options=chrome_options)

task_batch_size = 10

host = 'db-postgresql-sfo2-29804-do-user-1168167-0.a.db.ondigitalocean.com'
conn = psycopg2.connect(
        host=host,
        port=25060,
        dbname='defaultdb',
        user='doadmin',
        password=os.getenv('DO_DB_PASSWORD'))
cur = conn.cursor()
print('Successfully connected to {0}'.format(host))

def ask_google(query):
    # Search for query
    query = query.replace(' ', '+')
    driver.get('http://www.google.com/search?q=' + query)

    # Get HTML only
    return driver.find_element_by_xpath('//div[@id="search"]').get_attribute("outerHTML")

def crawl(i, question):
    html = ask_google(question)
    cur.execute('UPDATE queries SET html = %s WHERE id = %s;', [html, i])
    conn.commit()
    print('Retrieved HTML for question {0}: {1}'.format(i, question))

def do_tasks(tasks):
    for i, question in tasks:
        crawl(i, question)
        time.sleep(random.randint(2, 10))

while True:
    cur.execute('SELECT id, question FROM queries WHERE html IS NULL LIMIT %s;',
            [task_batch_size])
    do_tasks(cur.fetchmany(task_batch_size))
    print('Finished {0} tasks'.format(task_batch_size))
