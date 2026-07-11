import sqlite3


file="database.db"
create_tables=["""CREATE TABLE IF NOT EXISTS  USERS (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               username TEXT NOT NULL,
               password_hash TEXT NOT NULL,
               starting_balance REAL DEFAULT 10000.00,
               created_at DATETIME DEFAULT CURRENT_TIMESTAMP);""",
                """CREATE TABLE IF NOT EXISTS CRYPTOCURRENCIES(
                symbol PRIMARY KEY,
                name TEXT NOT NULL,
                current_price REAL NOT NULL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP);""",
                """CREATE TABLE IF NOT EXISTS  PORTFOLIOS (
               id INTEGER PRIMARY KEY,
               user_id INTEGER NOT NULL,
               crypto_symbol TEXT NOT  NULL,
                quantity REAL,
                average_buy_price REAL NOT NULL,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_USERS
                        FOREIGN KEY (user_id) 
                        REFERENCES USERS(id),
                CONSTRAINT fk_CRYPTOCURRENCIES
                    FOREIGN KEY (crypto_symbol) 
                    REFERENCES  CRYPTOCURRENCIES(symbol));""",
                """CREATE TABLE IF NOT EXISTS TRANSACTIONS(
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                crypto_symbol TEXT NOT NULL,
                transaction_type TEXT NOT NULL CHECK(transaction_type IN ("SELL","BUY")),
                quantity REAL NOT NULL CHECK(quantity>0),
                price_at_execution REAL  NOT NULL,
                total_value REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_USERS
                    FOREIGN KEY (user_id)
                    REFERENCES USERS(id),
                CONSTRAINT fk_CRYPTOCURRENCIES
                    FOREIGN KEY (crypto_symbol)
                    REFERENCES CRYPTOCURRENCIES(symbol));""",
                """CREATE TABLE IF NOT EXISTS PRICE_HISTORY(
                history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                crypto_symbol TEXT,
                open_price REAL NOT NULL,
                high_price REAL NOT NULL,
                low_price REAL NOT NULL,
                close_price REAL NOT NULL,
                volume REAL NOT NULL,
                timestamp DATETIME NOT NULL,
                timeframe TEXT NOT NULL CHECK(timeframe IN ("1m","5m","15m","1h","4h","1d")),
                CONSTRAINT fk_CRYPTOCURRENCIES
                    FOREIGN KEY (crypto_symbol)
                    REFERENCES CRYPTOCURRENCIES(symbol));"""]

try:
    with sqlite3.connect(file) as conn:
        
        print("Database formed")
        cursor= conn.cursor()

        for tables in create_tables:
            cursor.execute(tables)
        conn.commit()

        print("tables has been created succsefully")
        pass
except sqlite3.OperationalError as e :
    print("failed to open database", e)

print("TABLES STRUCTURE:")
tables_list=[conn.execute("PRAGMA table_info('USERS')"),conn.execute("PRAGMA table_info('CRYPTOCURRENCIES')"),
             conn.execute("PRAGMA table_info('PORTFOLIOS')"),conn.execute("PRAGMA table_info('TRANSACTIONS')"),
             conn.execute("PRAGMA table_info('PRICE_HISTORY')")]
counter=0
table_names=["USERS","CRYPTOCURRENCIES","PORTFOLIOS","TRANSACTIONS","PRICE_HISTORY"]
for i in tables_list:
    print(f"Table {table_names[counter]}:")
    counter+=1
    for j in i:
        print(j)

#inserting data
cursor.execute("""INSERT INTO USERS (username, password_hash) 
                        VALUES (?, ?)""", 
                 ('test_er', 'placeholder_hash'))
cursor.execute("""INSERT INTO CRYPTOCURRENCIES (symbol,name,current_price)
                       VALUES(?,?,?)""",
                  ('BTC','Bitcoin','88252.3') )
cursor.execute("""INSERT INTO PORTFOLIOS (user_id,crypto_symbol,quantity,average_buy_price)
                        VALUES(?,?,?,?)""",
                    ('1','BTC','10.2','88252.3'))
cursor.execute("""INSERT INTO TRANSACTIONS (user_id,crypto_symbol,transaction_type,quantity,price_at_execution,total_value)
                        VALUES(?,?,?,?,?,?)""",
                    ('1','BTC','BUY','5','88252.3','1000000'))

cursor.execute("""INSERT INTO TRANSACTIONS (user_id,crypto_symbol,transaction_type,quantity,price_at_execution,total_value)
                        VALUES(?,?,?,?,?,?)""",
                       ('2','BTC','BUY','5','88252.3','1000000'))
conn.commit()

#cleaning db for testing  
"""cursor.execute("DELETE  FROM USERS")
cursor.execute("DELETE FROM CRYPTOCURRENCIES")
cursor.execute("DELETE FROM PORTFOLIOS")
cursor.execute("DELETE FROM TRANSACTIONS")
conn.commit()"""
#Verify insertion
cursor.execute("SELECT * FROM USERS")
print(cursor.fetchall())
cursor.execute("SELECT * FROM CRYPTOCURRENCIES")
print(cursor.fetchall())
cursor.execute("SELECT * FROM PORTFOLIOS")
print(cursor.fetchall())
cursor.execute("SELECT * FROM TRANSACTIONS")
print(cursor.fetchall())
