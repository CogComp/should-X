import psycopg2
import os

def connect_to_gcp():
    host = '35.224.30.107'
    conn = psycopg2.connect(
        host=host,
        port=5432,
        dbname='postgres',
        user='postgres',
        password=os.getenv('DO_DB_PASSWORD'))
    cur = conn.cursor()

    return conn, cur
