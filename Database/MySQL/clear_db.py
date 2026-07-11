import mysql.connector
from mysql.connector import connect, Error

DB_NAME= "trading_simulator"

try:
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
    cursor.execute("SET FOREIGN_KEY_CHECKS=0")

    table_names=["USERS","CRYPTOCURRENCIES","PORTFOLIOS","TRANSACTIONS","PRICE_HISTORY"]

    for table in table_names:
        cursor.execute(f"TRUNCATE TABLE {table}")

    cursor.execute("SET FOREIGN_KEY_CHECKS=1")
    for table in table_names:
        print(f"Data in {table}:")
        cursor.execute(f"SELECT COUNT(*) FROM {table};")
        result = cursor.fetchone() 
        print(result)
    
    
    print("Database was cleared")
except mysql.connector.Error as err:
    print(f"Error: {err}")