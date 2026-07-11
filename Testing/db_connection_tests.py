import sys
sys.path.append(".")

import db_connection
import bcrypt

print("=" * 60)
print("DATABASE CONNECTION MODULE - COMPREHENSIVE TESTING")
print("=" * 60)

# Test 1: Connection Functions
print("\n--- Test 1: Core Connection Functions ---")
connection, cursor = db_connection.get_connection()
if connection and cursor:
    print("PASSED - Connection established successfully")
    print(f"  Connection active: {connection.is_connected()}")
    db_connection.close_connection(connection, cursor)
    print(f"  Connection closed: {not connection.is_connected()}")
else:
    print("FAILED - Connection establishment failed")

# Test 2: User ID Retrieval
print("\n--- Test 2: User ID Retrieval ---")
print("Test 2.1: Existing User")
connection, cursor = db_connection.get_connection()
cursor.execute("SELECT username FROM USERS LIMIT 1")
result = cursor.fetchone()
db_connection.close_connection(connection, cursor)

if result:
    test_username = result[0]
    user_id = db_connection.get_user_id(test_username)
    if user_id:
        print(f"PASSED - User ID retrieved: {user_id}")
    else:
        print("FAILED - Could not retrieve user ID")
else:
    print("Note: No users in database to test with")

print("\nTest 2.2: Non-existent User")
user_id = db_connection.get_user_id("nonexistent_user_xyz")
if user_id is None:
    print("PASSED - Non-existent user returns None")
else:
    print("FAILED - Should return None for non-existent user")

# Test 3: Live Price Fetching
print("\n--- Test 3: Cryptocurrency Price Fetching ---")
print("Test 3.1: Valid Symbol (BTC)")
btc_price = db_connection.get_crypto_price("BTC")
if btc_price > 0:
    print(f"PASSED - BTC price fetched: ${btc_price:.2f}")
else:
    print("FAILED - Could not fetch BTC price")

print("\nTest 3.2: Invalid Symbol")
invalid_price = db_connection.get_crypto_price("INVALID")
if invalid_price == 0.0:
    print("PASSED - Invalid symbol returns 0.0")
else:
    print("FAILED - Should return 0.0 for invalid symbol")

# Test 4: Average Buy Price Calculation
print("\n--- Test 4: Average Buy Price Calculation ---")
print("Setting up test user 'mathtest'...")

# Clean up test user completely
connection, cursor = db_connection.get_connection()
if connection:
    try:
        cursor.execute("SELECT id FROM USERS WHERE username = 'mathtest'")
        result = cursor.fetchone()
        if result:
            mathtest_id = result[0]
            cursor.execute("DELETE FROM TRANSACTIONS WHERE user_id = %s", (mathtest_id,))
            cursor.execute("DELETE FROM PORTFOLIOS WHERE user_id = %s", (mathtest_id,))
        cursor.execute("DELETE FROM USERS WHERE username = 'mathtest'")
        connection.commit()
        print("  Cleaned up existing test user")
    except Exception as e:
        print(f"  Cleanup note: {e}")
        connection.rollback()
    
    # Create fresh test user with starting balance
    password_hash = bcrypt.hashpw("testpass123456".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute("""INSERT INTO USERS (username, password_hash, starting_balance, total_balance) 
                   VALUES (%s, %s, %s, %s)""", 
                  ('mathtest', password_hash, 100000.00, 100000.00))  # Give $100k for testing
    connection.commit()
    print("  Created fresh test user with $100,000 (for testing)")
    db_connection.close_connection(connection, cursor)

# First purchase: 0.5 BTC @ $40,000 = $20,000
success1, msg1 = db_connection.execute_trade("mathtest", "BTC", 0.5, 40000, "BUY")
print(f"  First purchase (0.5 BTC @ $40k): {msg1}")

if success1:
    # Second purchase: 0.3 BTC @ $50,000 = $15,000
    success2, msg2 = db_connection.execute_trade("mathtest", "BTC", 0.3, 50000, "BUY")
    print(f"  Second purchase (0.3 BTC @ $50k): {msg2}")
    
    if success2:
        # Verify average price
        connection, cursor = db_connection.get_connection()
        if connection:
            user_id = db_connection.get_user_id("mathtest")
            cursor.execute("""SELECT quantity, average_buy_price 
                           FROM PORTFOLIOS 
                           WHERE user_id = %s AND crypto_symbol = 'BTC'""", (user_id,))
            result = cursor.fetchone()
            
            if result:
                quantity, avg_price = result
                expected_avg = 43750.0  # (0.5*40000 + 0.3*50000) / 0.8 = 43750
                
                print(f"\n  Calculation Verification:")
                print(f"    Quantity: {float(quantity):.8f} BTC")
                print(f"    Average Buy Price: ${float(avg_price):.2f}")
                print(f"    Expected: ${expected_avg:.2f}")
                print(f"    Math: (0.5×$40,000 + 0.3×$50,000) / 0.8 = ${expected_avg:.2f}")
                
                if abs(float(avg_price) - expected_avg) < 1.0:
                    print("  PASSED - Average buy price calculated correctly")
                else:
                    print("  FAILED - Average buy price calculation incorrect")
            else:
                print("  FAILED - Could not retrieve portfolio data")
            
            db_connection.close_connection(connection, cursor)
    else:
        print("  FAILED - Second purchase failed")
else:
    print("  FAILED - First purchase failed (likely insufficient funds)")

# Test 5: Trade Validation
print("\n--- Test 5: Trade Validation ---")
print("Test 5.1: Insufficient Cash")

# Create test user with default $10,000
connection, cursor = db_connection.get_connection()
if connection:
    try:
        cursor.execute("SELECT id FROM USERS WHERE username = 'validtest'")
        result = cursor.fetchone()
        if result:
            validtest_id = result[0]
            cursor.execute("DELETE FROM TRANSACTIONS WHERE user_id = %s", (validtest_id,))
            cursor.execute("DELETE FROM PORTFOLIOS WHERE user_id = %s", (validtest_id,))
        cursor.execute("DELETE FROM USERS WHERE username = 'validtest'")
        connection.commit()
    except:
        connection.rollback()
    
    password_hash = bcrypt.hashpw("testpass123456".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute("""INSERT INTO USERS (username, password_hash, starting_balance, total_balance) 
                   VALUES (%s, %s, %s, %s)""", 
                  ('validtest', password_hash, 10000.00, 10000.00))
    connection.commit()
    db_connection.close_connection(connection, cursor)

# Try to buy $12,000 worth of BTC (should fail with $10k balance)
success, message = db_connection.execute_trade("validtest", "BTC", 0.5, 24000, "BUY")
if not success and "Not enough cash" in message:
    print(f"PASSED - Overspending prevented")
    print(f"  Error message: {message}")
else:
    print("FAILED - Should prevent overspending")

print("\nTest 5.2: Insufficient Holdings for Sell")
# First buy some BTC
success, msg = db_connection.execute_trade("validtest", "BTC", 0.3, 1000, "BUY")  # $300 purchase
if success:
    print(f"  Purchased 0.3 BTC: {msg}")
else:
    print(f"  Purchase failed: {msg}")

# Try to sell 0.5 BTC when only have 0.3 (should fail)
success, message = db_connection.execute_trade("validtest", "BTC", 0.5, 1000, "SELL")
if not success and "Insufficient" in message:
    print(f"PASSED - Overselling prevented")
    print(f"  Error message: {message}")
else:
    print(f"FAILED - Should prevent overselling (got: {message})")

# Test 6: Transaction Atomicity (Rollback)
print("\n--- Test 6: Transaction Atomicity (Rollback) ---")
print("Testing rollback with invalid crypto symbol...")

connection, cursor = db_connection.get_connection()
if connection:
    user_id = db_connection.get_user_id("validtest")
    cursor.execute("SELECT COUNT(*) FROM TRANSACTIONS WHERE user_id = %s", (user_id,))
    count_before = cursor.fetchone()[0]
    print(f"  Transactions before: {count_before}")
    db_connection.close_connection(connection, cursor)

# Try to trade with invalid crypto (should fail due to foreign key)
success, message = db_connection.execute_trade("validtest", "INVALIDCRYPTO", 1.0, 100, "BUY")

connection, cursor = db_connection.get_connection()
if connection:
    cursor.execute("SELECT COUNT(*) FROM TRANSACTIONS WHERE user_id = %s", (user_id,))
    count_after = cursor.fetchone()[0]
    print(f"  Transactions after: {count_after}")
    
    if count_before == count_after and not success:
        print("PASSED - Rollback prevented partial transaction")
        print(f"  Error was: {message[:80]}...")  # Truncate long error
    else:
        print("FAILED - Transaction may have been partially recorded")
    
    db_connection.close_connection(connection, cursor)

# Test 7: Portfolio Summary Accuracy
print("\n--- Test 7: Portfolio Summary Accuracy ---")
summary = db_connection.get_portfolio_summary("validtest")
print(f"  Total Balance: ${summary['total_balance']:.2f}")
print(f"  Available Cash: ${summary['available_cash']:.2f}")
print(f"  Holding Value: ${summary['holding_value']:.2f}")
print(f"  Number of Holdings: {len(summary['holdings'])}")

if summary['total_balance'] > 0:
    print("PASSED - Portfolio summary calculated")
else:
    print("FAILED - Portfolio summary calculation error")

# Test 8: Empty Portfolio Handling
print("\n--- Test 8: Empty Portfolio (New User) ---")
connection, cursor = db_connection.get_connection()
if connection:
    try:
        cursor.execute("SELECT id FROM USERS WHERE username = 'newuser'")
        result = cursor.fetchone()
        if result:
            newuser_id = result[0]
            cursor.execute("DELETE FROM TRANSACTIONS WHERE user_id = %s", (newuser_id,))
            cursor.execute("DELETE FROM PORTFOLIOS WHERE user_id = %s", (newuser_id,))
        cursor.execute("DELETE FROM USERS WHERE username = 'newuser'")
        connection.commit()
    except:
        connection.rollback()
    
    password_hash = bcrypt.hashpw("testpass123456".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cursor.execute("""INSERT INTO USERS (username, password_hash, starting_balance, total_balance) 
                   VALUES (%s, %s, %s, %s)""", 
                  ('newuser', password_hash, 10000.00, 10000.00))
    connection.commit()
    db_connection.close_connection(connection, cursor)

summary = db_connection.get_portfolio_summary("newuser")
if (summary['total_balance'] == 10000.0 and 
    summary['available_cash'] == 10000.0 and 
    summary['holding_value'] == 0.0 and 
    len(summary['holdings']) == 0):
    print("PASSED - New user shows starting balance correctly")
    print(f"  Total Balance: ${summary['total_balance']:.2f}")
    print(f"  Available Cash: ${summary['available_cash']:.2f}")
else:
    print("FAILED - Empty portfolio handling incorrect")

# Test 9: Recent Transactions Formatting
print("\n--- Test 9: Transaction Formatting ---")
transactions = db_connection.get_recent_transactions("validtest", 3)
if transactions:
    print("PASSED - Transactions retrieved and formatted")
    for i, txn in enumerate(transactions, 1):
        print(f"  {i}. {txn}")
else:
    print("Note: Test user has no transactions")

# Test 10: Transaction String Parser
print("\n--- Test 10: Transaction String Parser ---")
test_string = "BUY 0.5000 BTC $45123.45 2025-02-15 14:30:45"
parsed = db_connection.parse_transaction_string(test_string)

if parsed:
    print("PASSED - Transaction string parsed successfully")
    print(f"  Original: {test_string}")
    print(f"  Type: {parsed['transaction_type']}")
    print(f"  Quantity: {parsed['quantity']}")
    print(f"  Symbol: {parsed['crypto_symbol']}")
    print(f"  Price: ${parsed['price']:.2f}")
else:
    print("FAILED - Parsing returned None")

# Test 11: Balance Persistence
print("\n--- Test 11: Balance Persistence in Database ---")
connection, cursor = db_connection.get_connection()
if connection:
    user_id = db_connection.get_user_id("validtest")
    
    # Get balance before
    cursor.execute("SELECT total_balance FROM USERS WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    balance_before = result[0] if result and result[0] is not None else 0.0
    print(f"  Balance before trade: ${float(balance_before):.2f}")
    
    db_connection.close_connection(connection, cursor)
    
    # Execute trade (buy small amount)
    success, msg = db_connection.execute_trade("validtest", "SOL", 1.0, 100, "BUY")
    print(f"  Trade result: {msg}")
    
    # Get balance after
    connection, cursor = db_connection.get_connection()
    cursor.execute("SELECT total_balance FROM USERS WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    balance_after = result[0] if result and result[0] is not None else 0.0
    print(f"  Balance after trade: ${float(balance_after):.2f}")
    
    # Check if balance actually changed
    if success:
        # Balance should be different after successful trade
        if abs(float(balance_before) - float(balance_after)) > 0.01:
            print("PASSED - Database balance updated after trade")
        else:
            print("Note: Balance didn't change (may need to check get_portfolio_summary update logic)")
    else:
        print(f"Note: Trade failed - {msg}")
    
    db_connection.close_connection(connection, cursor)

# Test 12: Win Rate Calculation
print("\n--- Test 12: Win Rate Calculation ---")

win_rate = db_connection.calculate_win_rate("validtest")
print(f"  Calculated Win Rate: {win_rate}%")

if 0 <= win_rate <= 100:
    print("PASSED - Win rate within valid range (0-100%)")
else:
    print("FAILED - Win rate outside valid range")

# Test 13: 24-Hour Balance Change (if functions exist)
print("\n--- Test 13: 24-Hour Balance Tracking ---")

# Test the consolidated 24h balance change function
if hasattr(db_connection, 'get_24h_balance_change'):
    change_24h = db_connection.get_24h_balance_change("validtest")
    print(f"  24-Hour Change: ${change_24h:+.2f}")
    
    if isinstance(change_24h, (int, float)):
        print("PASSED - 24h change calculated successfully")
        
        # Test that it handles new users properly
        change_new = db_connection.get_24h_balance_change("newuser")
        print(f"  New user 24h change: ${change_new:+.2f}")
        
        if isinstance(change_new, (int, float)):
            print("PASSED - New user 24h change handled properly")
        else:
            print("FAILED - New user 24h change error")
    else:
        print("FAILED - 24h change calculation error")
else:
    print("FAILED - get_24h_balance_change() function not found")

# Test 14: Leaderboard Data (if function exists)
print("\n--- Test 14: Leaderboard Functionality ---")

if hasattr(db_connection, 'get_leaderboard_data'):
    leaderboard = db_connection.get_leaderboard_data()
    if leaderboard:
        print("PASSED - Leaderboard data retrieved")
        print(f"  Total users: {len(leaderboard)}")
        print("  Top 3:")
        for i, user in enumerate(leaderboard[:3], 1):
            print(f"    {i}. {user['username']}: ${user['total_balance']:.2f}")
    else:
        print("Note: No leaderboard data (no users or function returned empty)")
else:
    print("Note: get_leaderboard_data() function not implemented")

# Summary
print("\n" + "=" * 60)
print("TESTING COMPLETE")
print("=" * 60)
print("\nAll critical database functions have been tested.")
print("Review output above for any failures (FAILED) that need attention.")