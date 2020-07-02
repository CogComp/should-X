#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import psycopg2
import os
import time
import random
import threading

task_batch_size = 10
concurrent_sessions = 3

host = 'db-postgresql-sfo2-29804-do-user-1168167-0.a.db.ondigitalocean.com'


class CrawlWindow(threading.Thread):
    count = 0

    def __init__(self):
        threading.Thread.__init__(self)

        CrawlWindow.count += 1
        self.id = CrawlWindow.count

        chrome_options = Options()
        chrome_options.add_argument("--window-size=1024x768")
        # chrome_options.add_argument("--headless")
        chrome_options.add_argument('log-level=3')
        self.driver = webdriver.Chrome(options=chrome_options)

        self.conn = psycopg2.connect(
            host=host,
            port=25060,
            dbname='defaultdb',
            user='doadmin',
            password=os.getenv('DO_DB_PASSWORD'))
        self.cur = self.conn.cursor()

        print('Window {0} successfully connected to {1}'.format(self.id, host))

    def ask_google(self, query):
        # Search for query
        query = query.replace(' ', '+')
        self.driver.get('http://www.google.com/search?q=' + query)

        # Get HTML only
        return self.driver.find_element_by_xpath('//div[@id="search"]').get_attribute("outerHTML")

    def crawl(self, i, question):
        html = self.ask_google(question)
        self.cur.execute('UPDATE queries SET html = %s WHERE id = %s;', [html, i])
        print('Window {2} retrieved HTML for question {0}: {1}'.format(i, question, self.id))

    def do_tasks(self, tasks):
        for i, question in tasks:
            self.crawl(i, question)
            time.sleep(random.randint(2, 10))

    def run(self):
        while True:
            self.cur.execute(
                    '''
                    SELECT id, question 
                    FROM queries 
                    WHERE html IS NULL 
                    FOR UPDATE SKIP LOCKED 
                    LIMIT %s;
                    ''',
                    [task_batch_size])
            self.do_tasks(self.cur.fetchmany(task_batch_size))
            # "for update skip locked" means that we shouldn't commit until all tasks
            # in a batch are done
            self.conn.commit()
            print('Window {1} finished {0} tasks'.format(task_batch_size, self.id))

for _ in range(concurrent_sessions):
    CrawlWindow().start()
