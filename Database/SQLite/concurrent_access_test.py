import sqlite3
import threading 
import time

def simulate_user_transaction(user_id,results  ):
    try:
        conn=sqlite3.connect("database.db",timeout=5.0)
        cursor=conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")

        #Simulate order placement
        cursor.execute("""INSERT INTO TRANSACTIONS
                       (user_id, crypto_symbol,transaction_type, quantity, price_at_execution, total_value)
                       VALUES(?,?,?,?,?,?)""",(user_id,'BTC','BUY',0.01,24000,240))
        conn.commit()
        results.append(f"Transaction {user_id}: SUCCESS")
        conn.close()
    except sqlite3.OperationalError as e:
        results.append(f"Transaction {user_id}: FAILED - {e}")
    
    except sqlite3.IntegrityError as e:
        results.append(f"Transaction {user_id}: FAILED - {e}")


#Test with 5 simultaneous users
results=[]
threads=[]

print("Testing concurrent access with 5 simultaneous transactions...")
start=time.time()

for i in range(1,6):
    thread=threading.Thread(target=simulate_user_transaction,args=(i,results))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

end=time.time()

print(f"Test completed in {end-start} seconds")
print("Results:")
for result in results:
    print(result)