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
print("Successful connection to database!")   

print("\nMySQL Performance Test")

#Single combined test - proves database is fast enough
queries=[("User Lookup","SELECT * FROM USERS WHERE username='Michel'"),
         ("Portfolio Display","""SELECT p.*,c.current_price FROM PORTFOLIOS p JOIN CRYPTOCURRENCIES c ON p.crypto_symbol=c.symbol 
         WHERE p.user_id=1;"""),
         ("Transaction History","SELECT * FROM TRANSACTIONS WHERE user_id=1 ORDER BY timestamp DESC")]

total_time=0
for query in queries:
    start=time.time()
    cursor.execute(query[1])
    cursor.fetchall()
    query_time=round(time.time()-start,5)
    total_time+=query_time
    print(f"{query[0]}: {query_time}s")

print(f"\n Average time: {round(total_time/len(queries),5)}")
    