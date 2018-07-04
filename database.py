import sqlite3
from flask_login import current_user
import datetime, time


conn = sqlite3.connect('protocols.db')

c = conn.cursor()

# create table
c.execute('CREATE TABLE IF NOT EXISTS Protocols (version_id INTEGER PRIMARY KEY, user, timestamp, JSON_text TEXT)')

import json
file = 'data.json'
with open(file) as f:
    json_file = f.read()
    #data = json.loads(json_file)
    #textfile = json.dumps(data)

now = str(datetime.datetime.now())
user = str(current_user)

c.execute("INSERT INTO Protocols (user, timestamp, JSON_text) VALUES (?,?,?)",
            (user, now, json_file,))

# Save (commit) the changes
conn.commit()

# close connection
conn.close()
