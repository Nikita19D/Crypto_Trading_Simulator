import mysql.connector
from mysql.connector import connect, Error
import requests
from datetime import datetime
import bcrypt

DB_CONFIG = {
    'host': "trading-simulator.chgu8gc0uejo.eu-west-2.rds.amazonaws.com",
    'user': "admin",
    'password': ")EF0T_oa0:N3",
    'port': 3306,
    'ssl_disabled': False,
    'connect_timeout': 30,
    'raise_on_warnings': True,
    'database': "trading_simulator"
}

STARTING_BALANCE=10000.00

#Connection to the database
def get_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()
        return connection, cursor
    except mysql.connector.Error as err:
        print(f"Error connecting to the database: {err}")
        return None, None  

def close_connection(connection, cursor):
    if cursor:
        cursor.close()
    if connection and connection.is_connected():
        connection.close()  

#authetification
def authenticate_user(username, password):
    pass

def get_user_id(username):
    connection, cursor = get_connection()
    if connection is None:
        return None
    try:
        cursor.execute("SELECT id FROM USERS WHERE username = %s", (username,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            print("User not found")
            return None
    except mysql.connector.Error as err:
        print(f"Error fetching user ID: {err}")
        return None
    finally:
        close_connection(connection, cursor)
#Portfolio Functions
def get_user_portfolio(username):
    #get user's complete portfolio info
    connection,cursor=get_connection()
    if connection is None:
        return None
    
    try:
        user_id=get_user_id(username)
        if user_id is None:
            return []
        
        cursor.execute("""
            SELECT crypto_symbol, quantity, average_buy_price, last_updated
            FROM PORTFOLIOS 
            WHERE user_id = %s AND quantity > 0""",(user_id,))
        
        holdings=[]
        for row in cursor.fetchall():
            holding={
                "crypto_symbol":row[0],
                "quantity":float(row[1]),
                "average_buy_price":float(row[2]),
                "last_updated":row[3]
            }
            holdings.append(holding)
        return holdings
    except mysql.connector.Error as err:
        print(f"Error fetching user portfolio: {err}")
        return []
    finally:
        close_connection(connection, cursor)

def get_crypto_price(symbol):
    #get current prices of crypto using bybit API
    try:
        api_symbol=symbol if symbol.endswith("USDT") else symbol+"USDT"

        url=f"https://api.bybit.com/v5/market/tickers"

        params={"category":"spot","symbol":api_symbol}
        
        response = requests.get(url,params=params,timeout=10)
        if response.status_code==200:
            data=response.json()
            if data['retCode']==0 and data['result']['list']:
                price=float(data['result']['list'][0]['lastPrice'])
                print(f"Current price of {symbol}: {price}")
                return price
            else:
                print(f"API error for {symbol}: {data.get('retMsg', 'Unknown error')}")
                return 0.0
        else:
            print(f"HTTP error for {symbol}: {response.status_code}")
            return 0.0
    except Exception as e:
        print(f"Error fetching crypto price for {symbol}: {e}")
        return 0.0

def update_crypto_price_in_db(symbol, price):
    #update the price of crypto in database
    connection,cursor=get_connection()
    if connection is None:
        return False
    
    try:
        #Check if crypto exists in database, if not add it
        cursor.execute("SELECT symbol FROM CRYPTOCURRENCIES WHERE symbol = %s", (symbol,))
        if not cursor.fetchone():
            #Add new crypto to database
            crypto_name=symbol.replace("USDT","")
            cursor.execute("INSERT INTO CRYPTOCURRENCIES (symbol,name, current_price,last_updated) VALUES (%s, %s, %s, %s)", (symbol,crypto_name, price, datetime.now()))
        else:
            #Update existing crypto price
            cursor.execute("UPDATE CRYPTOCURRENCIES SET current_price = %s, last_updated = %s WHERE symbol = %s", (price, datetime.now(), symbol))
        
        connection.commit()
        return True
    except Exception as e:
        print(f"Error updating crypto price in database for {symbol}: {e}")
        return False
    finally:
        close_connection(connection, cursor)   

def get_and_update_crypto_price(symbol):
    price=get_crypto_price(symbol)
    if price>0:
        update_crypto_price_in_db(symbol, price)
    return price

def calculate_portfolio_value(username):
    portfolio=get_user_portfolio(username)
    total_value=0.0
    for holding in portfolio:
        current_price=get_and_update_crypto_price(holding['crypto_symbol'])
        total_value+=holding['quantity']*current_price
    return total_value
    

def calculate_total_spent(username):
    portfolio=get_user_portfolio(username)
    total_spent=0.0
    for holding in portfolio:
        total_spent+=holding['quantity']*holding['average_buy_price']
    return total_spent

def execute_trade(username, crypto_symbol, quantity, price, transaction_type):
    #execute buy/sell trade and update portfolio in database
    connection,cursor=get_connection()
    if connection is None:
        return False, "Database connection failed"
    try:
        user_id=get_user_id(username)
        if user_id is None:
            print("User not found")
            return False, "User not found"
        
        total_value = round(quantity * price, 6)
        portfolio_data=get_portfolio_summary(username)

        if transaction_type=="BUY":
            #Check if user has enough cash
            if total_value > portfolio_data['available_cash']:
                print("Not enough cash to execute the trade")
                return False, "Not enough cash to execute the trade"
            
            # Insert transaction
            cursor.execute("""INSERT INTO TRANSACTIONS (user_id, crypto_symbol, transaction_type, quantity, price_at_execution, total_value, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""", (user_id, crypto_symbol, transaction_type, round(quantity, 8), round(price, 6), total_value, datetime.now()))

            #Update portfolio with new record
            # Check if portfolio record exists
            cursor.execute("""
                SELECT quantity, average_buy_price FROM PORTFOLIOS 
                WHERE user_id = %s AND crypto_symbol = %s
            """, (user_id, crypto_symbol))
            
            existing = cursor.fetchone()
            
            if existing:
                old_quantity, old_avg_price = existing
                new_quantity = round(float(old_quantity) + quantity, 8)
                new_avg_price = round((((float(old_quantity) * float(old_avg_price)) + (quantity * price)) / new_quantity), 6)
                
                cursor.execute("""
                    UPDATE PORTFOLIOS 
                    SET quantity = %s, average_buy_price = %s, last_updated = %s
                    WHERE user_id = %s AND crypto_symbol = %s""", (new_quantity, new_avg_price, datetime.now(), user_id, crypto_symbol))
            else:
                cursor.execute("""
                    INSERT INTO PORTFOLIOS (user_id, crypto_symbol, quantity, average_buy_price, last_updated)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, crypto_symbol, round(quantity, 8), round(price, 6), datetime.now()))
                
        elif transaction_type == 'SELL':
            # Check if user has enough of the crypto
            current_holding = 0
            for holding in portfolio_data['holdings']:
                if holding['symbol'] == crypto_symbol:
                    current_holding = holding['quantity']
                    break
            
            if quantity > current_holding:
                return False, f"Insufficient {crypto_symbol}. Available: {current_holding}, Required: {quantity}"
            
            # Insert transaction
            cursor.execute("""INSERT INTO TRANSACTIONS (user_id, crypto_symbol, transaction_type, quantity, price_at_execution, total_value, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""", (user_id, crypto_symbol, transaction_type, round(quantity, 8), round(price, 6), total_value, datetime.now()))

            # Update portfolio (reduce quantity)
            cursor.execute("""UPDATE PORTFOLIOS SET quantity = quantity - %s, last_updated = %s
                WHERE user_id = %s AND crypto_symbol = %s""", (round(quantity, 8), datetime.now(), user_id, crypto_symbol))
            
            # Remove if quantity becomes 0 or less
            cursor.execute("""DELETE FROM PORTFOLIOS 
                WHERE user_id = %s AND crypto_symbol = %s AND quantity <= 0""", (user_id, crypto_symbol))
        
        connection.commit()
        return True, f"{transaction_type} order executed successfully!"
    except Exception as e:
        connection.rollback()
        return False, f"Transaction failed: {e}"
    finally:
        close_connection(connection, cursor)

def get_transaction_history(username):
    connection,cursor=get_connection()
    if connection is None:
        return []
    
    try:
        user_id=get_user_id(username)
        if user_id is None:
            print("User not found")
            return []
        
        cursor.execute("""SELECT crypto_symbol, transaction_type, quantity, price_at_execution, total_value, timestamp 
            FROM TRANSACTIONS WHERE user_id = %s ORDER BY timestamp DESC""",(user_id,))
        
        transactions=[]
        for row in cursor.fetchall():
            transaction={
                "crypto_symbol":row[0],
                "transaction_type":row[1],
                "quantity":row[2],
                "price_at_execution":row[3],
                "total_value":row[4],
                "timestamp":row[5]
            }
            transactions.append(transaction)
        return transactions
    except mysql.connector.Error as err:
        print(f"Error fetching transaction history: {err}")
        return []
    finally:
        close_connection(connection, cursor)

def get_portfolio_summary(username):
    connection,cursor=get_connection()

    #returns full summary of user's portfolio including total balance, available cash and holdings details
    portfolio = get_user_portfolio(username)
    
    # Get user's actual starting balance from database
    user_id = get_user_id(username)
    if user_id is None:
        return {
            'total_balance': STARTING_BALANCE,
            'available_cash': STARTING_BALANCE,
            'holding_value': 0.0,
            'holdings': []
        }
    
    # Get user's starting balance from database
    cursor.execute("SELECT starting_balance FROM USERS WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    user_starting_balance = float(result[0]) if result and result[0] is not None else STARTING_BALANCE
    
    if not portfolio:
        return {
            'total_balance': user_starting_balance,
            'available_cash': user_starting_balance,
            'holding_value': 0.0,
            'holdings': []
        }
    
    # Calculate holdings value
    total_holding_value = 0.0
    holdings_list = []
    
    for holding in portfolio:
        symbol = holding['crypto_symbol']
        quantity = float(holding['quantity'])
        current_price = get_and_update_crypto_price(symbol)
        current_value = quantity * current_price
        
        total_holding_value += current_value
        
        holdings_list.append({
            'symbol': symbol,
            'quantity': float(quantity),
            'current_price': float(current_price),
            'current_value': float(current_value),
            'average_buy_price': float(holding['average_buy_price'])
        })
    
    # Calculate available cash using actual starting balance
    total_spent = calculate_total_spent(username)
    available_cash = user_starting_balance - total_spent
    total_balance = available_cash + total_holding_value

    try:
        cursor.execute("UPDATE USERS SET total_balance=%s WHERE username=%s",(round(total_balance,8),username))
        connection.commit()
    except Error as e:
        print(f"Unable to update total balance value:{e}")

    close_connection(connection, cursor)
    return {
        'total_balance': float(total_balance),
        'available_cash': float(available_cash),  
        'holding_value': float(total_holding_value),
        'holdings': holdings_list
    }

def get_recent_transactions(username, limit=5):
    #get last 5 transactions for trading screen
    connection, cursor = get_connection()
    if not connection:
        return []
    
    try:
        user_id = get_user_id(username)
        if not user_id:
            return []
        
        cursor.execute(""" SELECT crypto_symbol, transaction_type, quantity, price_at_execution, timestamp
            FROM TRANSACTIONS WHERE user_id = %s 
            ORDER BY timestamp DESC  LIMIT %s""", (user_id, limit))
        
        transactions = []
        for row in cursor.fetchall():
            crypto_symbol, transaction_type, quantity, price, timestamp = row
            # Format: "BUY 0.5 BTC $45000.00 2024-01-01 10:30:15"
            formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
            transactions.append(f"{transaction_type} {float(quantity):.4f} {crypto_symbol} ${float(price):.2f} {formatted_timestamp}")
        
        return transactions
        
    except Exception as e:
        print(f"Error getting transactions: {e}")
        return []
    finally:
        close_connection(connection, cursor)

def parse_transaction_string(transaction_string):
    #Parse transaction string - format: "BUY 0.5 BTC $45000.00 2024-01-01 10:30:15"
    #Returns: dict with keys: transaction_type, quantity, crypto_symbol, price, timestamp
    try:
        # Split the string into parts
        parts = transaction_string.split()
        
        if len(parts) >= 5:
            transaction_type = parts[0]  
            quantity = float(parts[1])   
            crypto_symbol = parts[2]    
            price = float(parts[3].replace('$', ''))  
            
            # Handle timestamp (could be date + time)
            if len(parts) >= 6:
                timestamp = f"{parts[4]} {parts[5]}"  # 2024-01-01 10:30:15
            else:
                timestamp = parts[4]  
            
            return {
                'transaction_type': transaction_type,
                'quantity': quantity,
                'crypto_symbol': crypto_symbol,
                'price': price,
                'timestamp': timestamp
            }
        else:
            # Return None if format doesn't match expected pattern
            return None
            
    except (ValueError, IndexError) as e:
        print(f"Error parsing transaction string '{transaction_string}': {e}")
        return None

def get_leaderboard_data():
    #getting leader board data - list of users with their total balance, sorted by balance descending
    connection, cursor = get_connection()
    if not connection:
        return []
    
    try:
        # Get all users with their stored total_balance, already sorted
        cursor.execute("SELECT username, total_balance FROM USERS ORDER BY total_balance DESC")
        users = cursor.fetchall()
        
        leaderboard = []
        for user_row in users:
            leaderboard.append({
                'username': user_row[0],
                'total_balance': float(user_row[1]) if user_row[1] is not None else STARTING_BALANCE
            })
        
        return leaderboard
        
    except Exception as e:
        print(f"Error getting leaderboard data: {e}")
        return []
    finally:
        close_connection(connection, cursor)

def get_24h_balance_change(username):
    #Get 24 hour balance change using stored 24_hour_price (handles update logic internally)
    connection, cursor = get_connection()
    if not connection:
        return 0.0
    
    try:
        user_id = get_user_id(username)
        if not user_id:
            return 0.0
            
        # Check if we need to update the 24h snapshot (once per day)
        cursor.execute("SELECT 24_hour_price, last_balance_update FROM USERS WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        
        # Update snapshot if needed (first time or 24+ hours passed)
        should_update = False
        if not result or result[0] is None or result[1] is None:
            should_update = True  # First time
        else:
            last_update = result[1]
            current_time = datetime.now()
            time_diff = current_time - last_update
            should_update = time_diff.total_seconds() >= 86400  # 24 hours
        
        if should_update:
            # Get current balance and update snapshot
            portfolio_data = get_portfolio_summary(username)
            current_balance = portfolio_data['total_balance']
            cursor.execute("UPDATE USERS SET 24_hour_price = %s, last_balance_update = %s WHERE id = %s", 
                          (round(current_balance, 2), datetime.now(), user_id))
            connection.commit()
            print(f"24h snapshot updated for {username}: ${current_balance:.2f}")
            return 0.0  # No change on first update
            
        # Get stored yesterday's balance
        yesterday_balance = float(result[0])
        
        # Get current balance
        portfolio_data = get_portfolio_summary(username)
        current_balance = portfolio_data['total_balance']
        
        # Calculate and return change amount
        change_amount = current_balance - yesterday_balance
        return round(change_amount, 2)
        
    except Exception as e:
        print(f"Error getting 24h change: {e}")
        return 0.0
    finally:
        close_connection(connection, cursor)

def calculate_win_rate(username):
    #Calculate win rate based on current holdings performance
    try:
        portfolio = get_user_portfolio(username)
        
        if not portfolio:
            return 0.0  # No holdings means 0% win rate
        
        profitable_count = 0
        total_count = len(portfolio)
        
        for holding in portfolio:
            symbol = holding['crypto_symbol']
            quantity = float(holding['quantity'])
            average_buy_price = float(holding['average_buy_price'])
            
            # Get current price with better error handling
            current_price = get_crypto_price(symbol)  # Don't update DB every time
            
            if current_price > 0:
                # Compare current value vs original cost
                current_value = quantity * current_price
                original_cost = quantity * average_buy_price
                is_profitable = current_value > original_cost
                
                # Debug info
                profit_loss = current_value - original_cost
                status = "PROFIT" if is_profitable else "LOSS"
                print(f"Win Rate Debug - {symbol}: ${original_cost:.2f} → ${current_value:.2f} = ${profit_loss:+.2f} ({status})")
                
                if is_profitable:
                    profitable_count += 1
        
        # Calculate win rate as percentage
        win_rate = (profitable_count / total_count) * 100 if total_count > 0 else 0.0
        return round(win_rate, 1)
        
    except Exception as e:
        print(f"Error calculating win rate: {e}")
        return 0.0  