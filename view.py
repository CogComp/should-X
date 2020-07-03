from flask import Flask, request, send_from_directory
import psycopg2
import os

app = Flask(__name__, static_url_path='')

host = 'db-postgresql-sfo2-29804-do-user-1168167-0.a.db.ondigitalocean.com'
conn = psycopg2.connect(
    host=host,
    port=25060,
    dbname='defaultdb',
    user='doadmin',
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
    return '''<html><body>{0}</body></html>'''.format(search_form())

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
