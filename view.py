from flask import Flask, request, send_from_directory
import psycopg2
import os

app = Flask(__name__, static_url_path='')

host = '35.224.30.107'
conn = psycopg2.connect(
    host=host,
    port=5432,
    dbname='postgres',
    user='postgres',
    password=os.getenv('DO_DB_PASSWORD'))
cur = conn.cursor()

def search_form(id = ''):
 return '''
    <form action="/questions" method="get">
        <label for="id">Enter question ID:</label>
        <input type="text" name="id" value="{0}">
        <input type="submit" value="Retrieve">
    </form>
    '''.format(id)

@app.route('/')
def welcome():
    cur.execute('SELECT count(*) FROM queries WHERE html IS NOT NULL;')
    scraped_count = cur.fetchone()[0]
    cur.execute('SELECT count(*) FROM queries;')
    all_count = cur.fetchone()[0]
    percentage = '{:.2f}'.format(scraped_count * 100.0 / all_count)
    scraped_str = '{:,}'.format(scraped_count)
    all_str = '{:,}'.format(all_count)
    return '''
        <html>
            <body>
                <label for="scrape">Scraped {0} / {1} ({2}%): </label>
                <progress id="scrape" value="{2}" max="100"></progress>
                {3}
            </body>
        </html>'''.format(scraped_str, all_str, percentage, search_form())

@app.route('/view.css')
def css():
    return send_from_directory('.', 'view.css')

@app.route('/questions')
def show_html():
    id = int(request.args.get('id'))
    cur.execute('SELECT question, html FROM queries WHERE id = %s;', [id])
    question, html = cur.fetchone()
    return '''
        <html>
            <head>
                <link rel="stylesheet" type="text/css" href="/view.css">
            </head>
            <body>
                {2}
                <h1 id="question">{0}</h1>
                {1}
            </body>
        </html>
    '''.format(question, html, search_form(id))
