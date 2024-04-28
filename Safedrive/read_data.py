import sqlite3
import json

# Connect to SQLite database
conn = sqlite3.connect('traffic_data.db')

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Execute a SELECT query to retrieve data
cursor.execute('SELECT * FROM traffic_data')

# Fetch the result
result = cursor.fetchall()

# Check the data
for row in result:
    # Assuming each row contains JSON data as a string
    data = row[1]  # Assuming JSON data is in the second column (index 1)
    
    # Convert JSON string to dictionary
    json_data = json.loads(data)
    
    # Check if 'some_key' exists in the JSON data before accessing it
    if 'some_key' in json_data and json_data['some_key'] == 'some_value':
        print("Data meets condition:", json_data)

# Close the connection
conn.close()
