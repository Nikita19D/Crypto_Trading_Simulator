import mysql.connector
from mysql.connector import connect, Error

    
DB_NAME= "trading_simulator"

try: 
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

    try:
        #adding unique constraint to USERS table
        #cursor.execute("""ALTER TABLE USERS 
        #           ADD CONSTRAINT unique_username UNIQUE (username)""")
            # Fix all problematic columns
        """cursor.execute("ALTER TABLE TRANSACTIONS MODIFY COLUMN total_value DECIMAL(30,8);")
        cursor.execute("ALTER TABLE TRANSACTIONS MODIFY COLUMN quantity DECIMAL(30,12);")  # Add this
        cursor.execute("ALTER TABLE TRANSACTIONS MODIFY COLUMN price_at_execution DECIMAL(20,8);")  # Add this
        
        # Also fix PORTFOLIOS table
        cursor.execute("ALTER TABLE PORTFOLIOS MODIFY COLUMN quantity DECIMAL(30,12);")  # Add this
        cursor.execute("ALTER TABLE PORTFOLIOS MODIFY COLUMN average_buy_price DECIMAL(20,8);")  # Add this
        
        #ADD 24 HOUR CHANGE PRICE TO USERS TABLE
        cursor.execute("ALTER TABLE USERS ADD 24_hour_price DECIMAL(15,2) DEFAULT 10000.00;")
        #add total_balance
        cursor.execute("ALTER TABLE USERS ADD total_balance DECIMAL(15,2) DEFAULT 10000.00;")

        #alter them to match total_value
        cursor.execute("ALTER TABLE USERS MODIFY COLUMN 24_hour_price DECIMAL(30,8);")
        cursor.execute("ALTER TABLE USERS MODIFY COLUMN total_balance DECIMAL(30,8);")"""
        
        # Add timestamp column for 24h balance tracking
        cursor.execute("ALTER TABLE USERS ADD COLUMN last_balance_update DATETIME DEFAULT CURRENT_TIMESTAMP;")

        # Add completed_modules column for learning progress tracking
        cursor.execute("ALTER TABLE USERS ADD COLUMN completed_modules VARCHAR(20) DEFAULT '';")

        connection.commit()
    except mysql.connector.Error as err:
        if err.errno==1061:#ducplicate key name
            print("Constraint already exists, skipping.")
        else:
            raise
except mysql.connector.Error as err:
    print(f"Failed altering database: {err}")

#ensures that connections are closed no matter what
finally:
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'connection' in locals() and connection.is_connected():
        connection.close()
