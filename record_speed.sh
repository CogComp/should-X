psql -U postgres -d postgres -h 35.224.30.107 -c 'INSERT INTO progress (time, scraped_count) VALUES (CURRENT_TIMESTAMP, (SELECT COUNT(*) FROM queries WHERE html IS NOT NULL));'
