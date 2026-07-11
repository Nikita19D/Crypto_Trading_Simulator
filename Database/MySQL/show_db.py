import mysql.connector
from mysql.connector import connect, Error
import time

DB_NAME= "trading_simulator"


#connection to specific db
connection = mysql.connector.connect(
      host="trading-simulator.chgu8gc0uejo.eu-west-2.rds.amazonaws.com",
      user="admin",
      password=")EF0T_oa0:N3",
      port=3306,
      ssl_disabled=False,
      connect_timeout=30,
      raise_on_warnings=True,
      database=DB_NAME
    )

cursor = connection.cursor()

cursor.execute("SELECT * FROM USERS;")
users=cursor.fetchall()
print(users)
cursor.close()
connection.close()