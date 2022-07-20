import pymysql
  
conn = pymysql.connect(host='localhost',user='root',password = "pass",db='College',)

cur = conn.cursor()
cur.execute("show databases")
output = cur.fetchall()
print(output)

# To close the connection
conn.close()
