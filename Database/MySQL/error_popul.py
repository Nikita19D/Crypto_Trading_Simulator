import mysql.connector
from mysql.connector import connect, Error
import time

DB_NAME= "trading_simulator"

try:
    #connection to specific db
    connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password=")EF0T_oa0:N3",
    database=DB_NAME
    )
    
    cursor = connection.cursor()
    print("Successful connection to database!")

    #Populating USERS   
    cursor.execute("INSERT INTO USERS (username,password_hash) VALUES(%s,%s)",('Michel','hashed_password_1'))
    cursor.execute("INSERT INTO USERS (username,password_hash) VALUES(%s,%s)",('Marko','hashed_password_2'))
    cursor.execute("INSERT INTO USERS (username,password_hash ) VALUES(%s,%s)",('Ben','hashed_password_3'))

    
    #Populating CRYPTOCURRENCIES
    cryptocurrencies=[('BTC','Bitcoin',78058.46),
                      ('ETH','Ethereum',2370.13),
                      ('SOL','Solana',104.01),
                      ('DOGE','Dogecoin',0.11),
                      ('BNB','Binance Coin',759.97)]
    
    for crypto in cryptocurrencies:
        cursor.execute("INSERT INTO CRYPTOCURRENCIES (symbol,name,current_price) VALUES(%s,%s,%s)",(crypto[0],crypto[1],crypto[2]))

    #Populating PORTFOLIOS
    cursor.execute("INSERT INTO PORTFOLIOS (user_id,crypto_symbol,quantity,average_buy_price) VALUES(%s,%s,%s,%s)",(1,'BTC',0.5,78058.4))
    cursor.execute("INSERT INTO PORTFOLIOS (user_id,crypto_symbol,quantity,average_buy_price) VALUES(%s,%s,%s,%s)",(2,'ETH',2,2370.13))

    #Populating TRANSACTIONS
    cursor.execute("INSERT INTO TRANSACTIONS (user_id,crypto_symbol,transaction_type,quantity,price_at_execution,total_value) VALUES (%s,%s,%s,%s,%s,%s)",
                   (1,'BTC','BUY',0.5,78058.46,39029.23))
    cursor.execute("INSERT INTO TRANSACTIONS (user_id,crypto_symbol,transaction_type,quantity,price_at_execution,total_value) VALUES (%s,%s,%s,%s,%s,%s)",
                   (2,'ETH','BUY',2,2370.13,4740.26))
    
    #Populating PRICE_HISTORY
    cursor.execute("INSERT INTO PRICE_HISTORY (crypto_symbol,open_price,high_price,low_price,close_price,volume,timestamp,timeframe) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                   ('BTC',78720.60,79355.00,78004.70,78471.70,15000000.0,'2025-01-19 11:26:39','1m'))

    connection.commit()
    cursor.close()
    connection.close()
   

except mysql.connector.Error as err:
    print(f"Failed creating database: {err}")