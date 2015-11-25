import sqlite3

DB = 'var/sqlite3.db'
conn = sqlite3.connect(DB)
cursor = conn.cursor()

print "users"
for row in cursor.execute("SELECT * FROM users"):
	print row
	
print "blogables"
for row in cursor.execute("SELECT * FROM blogables"):
	print row