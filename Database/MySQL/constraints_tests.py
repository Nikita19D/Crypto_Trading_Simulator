import mysql.connector
from mysql.connector import connect, Error
import time

DB_NAME= "trading_simulator"


#connection to specific db
connection = mysql.connector.connect(
host="localhost",
user="root",
password=")EF0T_oa0:N3",
database=DB_NAME
)

cursor = connection.cursor()
print("Successful connection to database!")

#Test 1: ENUM Constraint - Invalid Transaction type
print("\nTest 1: ENUM Constraint(transaction_type validation)")
try:  
    cursor.execute("INSERT INTO TRANSACTIONS (user_id,crypto_symbol,transaction_type,quantity,price_at_execution,total_value) VALUES (%s,%s,%s,%s,%s,%s)",
                (1,'ETH','TRADE',2,2370.13,4740.26))
    connection.commit()
    print("Failed - ENUM constraint not enforced")
except mysql.connector.DatabaseError as err:
    print("Passed - ENUM constraint enforced")
    print(f"Error: {err}")
except mysql.connector.IntegrityError as err:
    print("Passed - Constraint enforced")
    print(f"Error: {err}")

#Test 2: ENUM Constraint - Invalid Timeframe
print("\nTest 2: ENUM Constraint(timeframe validation)")
try:  
    cursor.execute("INSERT INTO PRICE_HISTORY (crypto_symbol,open_price,high_price,low_price,close_price,volume,timestamp,timeframe) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                ('BTC',78720.60,79355.00,78004.70,78471.70,15000000.0,'2025-01-19 11:26:39','3m'))
    connection.commit()
    print("Failed - ENUM constraint not enforced")
except mysql.connector.DatabaseError as err:
    print("Passed - ENUM constraint enforced")
    print(f"Error: {err}")
except mysql.connector.IntegrityError as err:
    print("Passed - Constraint enforced")
    print(f"Error: {err}")

#Test 3: NOT NULL Constraint - Missing Username
print("\nTest 3: NOT NULL Constraint(username required)")
try:  
    cursor.execute("INSERT INTO USERS (username,password_hash) VALUES(%s,%s)",(None,'hashed_password_1'))
    connection.commit()
    print("Failed - NOT NULL constraint not enforced")
except mysql.connector.IntegrityError as err:
    print("Passed - NOT NULL Constraint enforced")
    print(f"Error: {err}")

#Test 4: NOT NULL Constraint - Missing quantity
print("\nTest 4: NOT NULL Constraint(quantity required)")
try:  
    cursor.execute("INSERT INTO TRANSACTIONS (user_id,crypto_symbol,transaction_type,quantity,price_at_execution,total_value) VALUES (%s,%s,%s,%s,%s,%s)",
                   (1,'ETH','BUY',None,2370.13,4740.26))
    connection.commit()
    print("Failed - NOT NULL constraint not enforced")
except mysql.connector.IntegrityError as err:
    print("Passed - NOT NULL Constraint enforced")
    print(f"Error: {err}")

#Test 5: Foreign Key - PRICE_HISTORY->CRYPTOCURRENCIES
print("\nTest 5: Foreign Key Constraint(PRICE_HISTORY->CRYPTOCURRENCIES)")
try:  
    cursor.execute("INSERT INTO PRICE_HISTORY (crypto_symbol,open_price,high_price,low_price,close_price,volume,timestamp,timeframe) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                   ('INVALID',78720.60,79355.00,78004.70,78471.70,15000000.0,'2025-01-19 11:26:39','1m'))
    connection.commit()
    print("Failed - Foreign Key constraint not enforced")
except mysql.connector.IntegrityError as err:
    print("Passed - Foreign Key Constraint enforced")
    print(f"Error: {err}")

#Test 6: CASCADE DELETE Operations
print("\nTest 6: CASCADE DELETE(User Deletion Removes Related Data)")

#Create User
cursor.execute("INSERT INTO USERS (username,password_hash) VALUES(%s,%s)",('cascade_test_user','test_hash'))
connection.commit()

#Get the assigned user ID
test_user_id = cursor.lastrowid
print(f"Created test user with ID:{test_user_id}")

#Add portfolio for test user
cursor.execute("INSERT INTO PORTFOLIOS (user_id,crypto_symbol,quantity,average_buy_price) VALUES(%s,%s,%s,%s)",(test_user_id,'BTC',0.5,78058.4))

#Add transaction for test user
cursor.execute("INSERT INTO TRANSACTIONS (user_id,crypto_symbol,transaction_type,quantity,price_at_execution,total_value) VALUES (%s,%s,%s,%s,%s,%s)",
                (test_user_id,'BTC','BUY',0.5,78058.46,39029.23))

connection.commit()

#Counting records before deletion
cursor.execute("SELECT COUNT(*) FROM PORTFOLIOS WHERE user_id=%s",(test_user_id,))
portfolio_before=cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM TRANSACTIONS WHERE user_id=%s",(test_user_id,))
transactions_before=cursor.fetchone()[0]

print(f"Before deletion: {portfolio_before} portfolio record(s), {transactions_before} transaction(s)")

#Deleting user - all reocords related to user should be deleted
cursor.execute("DELETE FROM USERS WHERE id=%s",(test_user_id,))
connection.commit()

#Counting related record after deletion(should be none)
cursor.execute("SELECT COUNT(*) FROM PORTFOLIOS WHERE user_id=%s",(test_user_id,))
portfolio_after=cursor.fetchone()[0]
cursor.execute("SELECT COUNT(*) FROM TRANSACTIONS WHERE user_id=%s",(test_user_id,))
transactions_after=cursor.fetchone()[0]

print(f"After deletion: {portfolio_after} portfolio record(s), {transactions_after} transaction(s)")

if portfolio_after==0 and transactions_after==0:
    print("Passed - CASCADE DELETE successfully removed all related records")
else:
    print("Failed - Related records were not deleted")

cursor.close()
connection.close()