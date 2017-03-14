#!/usr/bin/python

import MySQLdb

# Open database connection
db = MySQLdb.connect("localhost","vichaark_signup","modi is great","vichaark_bblabs" )

# prepare a cursor object using cursor() method
cursor = db.cursor()

# execute SQL query using execute() method.
cursor.execute("SELECT VERSION()")

# Fetch a single row using fetchone() method.
data = cursor.fetchone()

print "Database version : %s " % data

#select emails
cursor.execute("SELECT * from registered_users")
for data in cursor.fetchall():
    print data

# disconnect from server
db.close()
