import sqlite3
import json

# Connect to SQLite database (creates it if not exists)
conn = sqlite3.connect('traffic_data.db')

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Create a table
cursor.execute('''CREATE TABLE IF NOT EXISTS traffic_data
                (id INTEGER PRIMARY KEY, data TEXT)''')

# Load JSON data from file
with open('traffic_data.json') as file:
    data = json.load(file)

# Insert data into SQLite
cursor.execute('INSERT INTO traffic_data (data) VALUES (?)', (json.dumps(data),))

# Commit changes and close connection
conn.commit()
conn.close()
