import psycopg2

hostname = ""
username = ""
password = ""
db = ""
conn_string = "dbname='%s' user='%s' host='%s' password='%s'" % (db, username, hostname, password)

conn = psycopg2.connect(conn_string)
print("Done")
