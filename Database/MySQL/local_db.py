import mysql.connector
from mysql.connector import connect, Error

DB_NAME= "trading_simulator"

TABLES = ["""CREATE TABLE IF NOT EXISTS USERS (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            starting_balance DECIMAL(15,2) DEFAULT 10000.00,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP) ;""",

     """CREATE TABLE IF NOT EXISTS CRYPTOCURRENCIES (
            symbol VARCHAR(10) PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            current_price DECIMAL(15,6) NOT NULL,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP);""",

    """CREATE TABLE IF NOT EXISTS PORTFOLIOS (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            crypto_symbol VARCHAR(10) NOT NULL,
            quantity DECIMAL(20,8) NOT NULL,
            average_buy_price DECIMAL(15,6) NOT NULL,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT fk_portfolio_user
                FOREIGN KEY (user_id)
                REFERENCES USERS(id)
                ON DELETE CASCADE,

            CONSTRAINT fk_portfolio_crypto
                FOREIGN KEY (crypto_symbol)
                REFERENCES CRYPTOCURRENCIES(symbol)
                ON DELETE CASCADE);""",

    """CREATE TABLE IF NOT EXISTS TRANSACTIONS (
            transaction_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            crypto_symbol VARCHAR(10) NOT NULL,
            transaction_type ENUM('SELL','BUY') NOT NULL,
            quantity DECIMAL(20,8) NOT NULL,
            price_at_execution DECIMAL(15,6) NOT NULL,
            total_value DECIMAL(20,2) NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT fk_transaction_user
                FOREIGN KEY (user_id)
                REFERENCES USERS(id)
                ON DELETE CASCADE,

            CONSTRAINT fk_transaction_crypto
                FOREIGN KEY (crypto_symbol)
                REFERENCES CRYPTOCURRENCIES(symbol)
                ON DELETE CASCADE);""",

    """CREATE TABLE IF NOT EXISTS PRICE_HISTORY (
            history_id INT AUTO_INCREMENT PRIMARY KEY,
            crypto_symbol VARCHAR(10) NOT NULL,
            open_price DECIMAL(15,6) NOT NULL,
            high_price DECIMAL(15,6) NOT NULL,
            low_price DECIMAL(15,6) NOT NULL,
            close_price DECIMAL(15,6) NOT NULL,
            volume DECIMAL(30,6) NOT NULL,
            timestamp DATETIME NOT NULL,
            timeframe ENUM('1m','5m','15m','1h','4h','1d') NOT NULL,

            CONSTRAINT fk_price_crypto
                FOREIGN KEY (crypto_symbol)
                REFERENCES CRYPTOCURRENCIES(symbol)
                ON DELETE CASCADE);"""
]
try:
    """#db intialization
    connection = mysql.connector.connect(
      host="localhost",
      user="root",
      password=")EF0T_oa0:N3")
    
    cursor = connection.cursor()

    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
    print(f"Database {DB_NAME} created successfully.")

    cursor.close()
    connection.close()"""
    #connection to specific db
    connection = mysql.connector.connect(
      host="localhost",
      user="root",
      password=")EF0T_oa0:N3",
      database=DB_NAME
    )
    
    cursor = connection.cursor()

    for table in TABLES:
        cursor.execute(table)
    
    connection.commit()
    print("All tables created successfully!")

    table_names=["USERS","CRYPTOCURRENCIES","PORTFOLIOS","TRANSACTIONS","PRICE_HISTORY"]

    for table_name in table_names:
        print(f"Table {table_name}")

        cursor.execute(f"DESCRIBE {table_name}")
        columns=cursor.fetchall()
        
        for col in columns:
            print(f"{col[0]}: {col[1]}")
        print("="*40)

    cursor.close()
    connection.close()
    
except mysql.connector.Error as err:
    print(f"Failed creating database: {err}")