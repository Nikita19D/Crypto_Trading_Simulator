import sqlite3

conn=sqlite3.connect("database.db")
cursor=conn.cursor()

cursor.execute("PRAGMA foreign_keys=ON")

print("SQLITE BASIC CONSTRAINT VALIDATION")

#Test 1: Foreign Key
print("Test 1: Foreign Key Constraint (PORTFOLIOS -> USERS)")
try:
    cursor.execute("""INSERT INTO PORTFOLIOS
                   (user_id,crypto_symbol,quantity,average_buy_price)
                   VALUES(?,?,?,?)""",(999, 'BTC', 0.5, 24000))
    conn.commit()    
    print("Failed- Foreign key not enforced ")
except sqlite3.IntegrityError as e:
    print(f"Passed - {e}")

#Test 2: CHECK Constraint 
print("Test 2: CHECK Constraint (transaction_type validation)")
try:
    cursor.execute("""INSERT INTO TRANSACTIONS (user_id, crypto_symbol, transaction_type, quantity, price_at_execution, total_value)
                   VALUES(?,?,?,?,?,?)""",(1,"BTC","INVALID",0.1,24000,2400))
    
    conn.commit()
    print("Failed - CHECK constraint not enforced ")
except sqlite3.IntegrityError as e:
    print(f"Passed - {e}")

#Test 3: UNIQUE Constraint
print("Test 3: UNIQUE Constraint (username uniqueness)")
try:
    cursor.execute("""INSERT INTO USERS (username, password_hash) 
                      VALUES (?, ?)""",("test_user","another_user"))
    print("FAILED - UNIQUE Constraint not enforced")    
except sqlite3.IntegrityError as e:
    print(f"Passed - {e}")