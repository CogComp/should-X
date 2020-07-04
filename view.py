from flask import Flask, request, send_from_directory
import psycopg2
import pytz
import gcp

app = Flask(__name__, static_url_path='')

pst = pytz.timezone("US/Pacific")

conn, cur = gcp.connect_to_gcp()

def search_form(id = '', query = ''):
 return '''
    <form action="/questions" method="get">
        <label for="id">Enter question ID:</label>
        <input type="text" name="id" value="{0}">
        <input type="submit" value="Retrieve">
    </form>
    <form action="/search" method="get">
        <label for="query">Or enter in exact substring query:</label>
        <input type="text" name="query" value="{1}">
        <input type="submit" value="Search">
    </form>
    '''.format(id, query)

@app.route('/')
def welcome():
    cur.execute('SELECT count(*) FROM queries WHERE html IS NOT NULL;')
    scraped_count = cur.fetchone()[0]
    cur.execute('SELECT count(*) FROM queries;')
    all_count = cur.fetchone()[0]
    percentage = '{:.2f}'.format(scraped_count * 100.0 / all_count)
    scraped_str = '{:,}'.format(scraped_count)
    all_str = '{:,}'.format(all_count)

    cur.execute('SELECT time, scraped_count FROM progress ORDER BY time DESC LIMIT 2;')
    time2, count2 = cur.fetchone()
    time1, count1 = cur.fetchone()

    latest = time2.astimezone(pst)
    latest_str = latest.strftime('%Y-%m-%d %H:%M:%S %Z')
    time_diff = (time2 - time1).total_seconds()
    speed = (count2 - count1) * 1.0 / time_diff

    remaining_scrapes = all_count - scraped_count
    remaining_seconds = remaining_scrapes / speed
    remaining_days = remaining_seconds / 3600 / 24

    return '''
        <html>
            <body>
                <div class="progress">
                    <label for="scrape">Scraped {0} / {1} ({2}%): </label>
                    <progress id="scrape" value="{2}" max="100"></progress>
                </div>
                Speed: {5:.2f} scrapes / second => {6:.2f} days remaining (Last updated at {3})
                {4}
            </body>
        </html>'''.format(scraped_str, all_str, percentage, latest_str, search_form(), speed, remaining_days)

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

@app.route('/search')
def show_search():
    query = request.args.get('query')
    cur.execute(
            'SELECT id, question FROM queries WHERE html IS NOT NULL AND STRPOS(question, %s) > 0 LIMIT 10;', 
            [query])
    results_str = ''
    for id, question in cur.fetchall():
        results_str += '<li><a href="/questions?id={0}">{1}</a></li>'.format(id, question)
    return '''
        <html>
            <body>
                {2}
                <h1>Scraped questions that have "{0}" as a substring:</h1>
                <ul>{1}</ul>
            </body>
        </html>
    '''.format(query, results_str, search_form(query=query))
