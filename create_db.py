"""
Creates a sqlite db with the appropriate schema
to work with the review anything web app.
"""
import sqlite3

# change this to whatever you'd like
# just don't forget to change the config.json file!
FILE_NAME = 'review_anything_db.sqlite'
SQL_FILE = 'db_schema.sql'

# create an empty file
with open(FILE_NAME, 'w') as _:
    pass

with sqlite3.connect(FILE_NAME) as conn:
    cursor = conn.cursor()

    cursor.executescript(open(SQL_FILE).read())

    conn.commit()
