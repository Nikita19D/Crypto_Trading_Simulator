from PySide6.QtWidgets import QApplication

import sys
sys.path.append(".")
import db_connection

app = QApplication(sys.argv)

print("=" * 50)
print("Portfolio Screen Tests")
print("=" * 50)

# test 1 - loading portfolio summary
print("\nTest 1: Portfolio Summary Load")
try:
    data = db_connection.get_portfolio_summary("superuser")
    if 'total_balance' not in data:
        raise Exception("Missing total_balance")
    if 'available_cash' not in data:
        raise Exception("Missing available_cash")
    if 'holdings' not in data:
        raise Exception("Missing holdings")
    if not isinstance(data['holdings'], list):
        raise Exception("Holdings should be a list")
    print(f"  Total Balance: ${data['total_balance']:.2f}")
    print(f"  Available Cash: ${data['available_cash']:.2f}")
    print(f"  Holdings count: {len(data['holdings'])}")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 2 - checking 24h balance change
print("\nTest 2: 24h Balance Change")
try:
    change = db_connection.get_24h_balance_change("superuser")
    if not isinstance(change, float):
        raise Exception("Should return float")
    prefix = "+" if change >= 0 else "-"
    print(f"  24h Change: {prefix}${abs(change):.2f}")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 3 - win rate should be between 0 and 100
print("\nTest 3: Win Rate Calculation")
try:
    win_rate = db_connection.calculate_win_rate("superuser")
    if win_rate < 0.0 or win_rate > 100.0:
        raise Exception(f"Win rate should be 0-100, got {win_rate}")
    print(f"  Win Rate: {win_rate}%")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 4 - parsing transaction strings
print("\nTest 4: Transaction String Parsing")
try:
    # test a valid BUY string
    valid = "BUY 0.5000 BTC $45000.00 2025-02-10 14:30:15"
    parsed = db_connection.parse_transaction_string(valid)
    if parsed is None:
        raise Exception("Valid string returned None")
    if parsed['transaction_type'] != "BUY":
        raise Exception("Type should be BUY")
    if parsed['quantity'] != 0.5:
        raise Exception("Quantity should be 0.5")
    if parsed['crypto_symbol'] != "BTC":
        raise Exception("Symbol should be BTC")
    if parsed['price'] != 45000.00:
        raise Exception("Price should be 45000")
    print(f"  Parsed type: {parsed['transaction_type']}")
    print(f"  Parsed symbol: {parsed['crypto_symbol']}")
    print(f"  Parsed price: ${parsed['price']:.2f}")

    # test a SELL string
    sell = "SELL 0.2500 ETH $2350.75 2025-02-10 15:00:00"
    parsed_sell = db_connection.parse_transaction_string(sell)
    if parsed_sell['transaction_type'] != "SELL":
        raise Exception("Should parse as SELL")
    if parsed_sell['crypto_symbol'] != "ETH":
        raise Exception("Should parse ETH")
    print(f"  SELL transaction parsed correctly")

    # test a broken string
    bad = "INVALID DATA"
    parsed_bad = db_connection.parse_transaction_string(bad)
    if parsed_bad is not None:
        raise Exception("Malformed string should return None")
    print(f"  Malformed string returns None")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 5 - loading recent transactions
print("\nTest 5: Transaction History")
try:
    transactions = db_connection.get_recent_transactions("superuser", 15)
    if not isinstance(transactions, list):
        raise Exception("Should return a list")
    if len(transactions) > 15:
        raise Exception("Should return max 15")
    print(f"  Retrieved {len(transactions)} transactions")

    if transactions:
        failed_parses = 0
        for t in transactions:
            if db_connection.parse_transaction_string(t) is None:
                failed_parses += 1
        print(f"  Successfully parsed: {len(transactions) - failed_parses}/{len(transactions)}")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 6 - what happens with a user that doesnt exist
print("\nTest 6: New User - Empty Portfolio")
try:
    data = db_connection.get_portfolio_summary("nonexistent_user_xyz")
    if data['total_balance'] != 10000.0:
        raise Exception("Should return starting balance")
    if data['available_cash'] != 10000.0:
        raise Exception("Should return starting cash")
    if data['holdings'] != []:
        raise Exception("Holdings should be empty")
    print(f"  Empty portfolio returns starting balance: ${data['total_balance']:.2f}")
    print(f"  Holdings list is empty: {data['holdings']}")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 7 - checking the color logic for 24h change
print("\nTest 7: 24h Change Color Logic")
try:
    change = db_connection.get_24h_balance_change("superuser")
    if change >= 0:
        expected_prefix = "+"
        expected_style = "green"
    else:
        expected_prefix = "-"
        expected_style = "red"
    print(f"  Change: ${change:.2f}")
    print(f"  Expected prefix: '{expected_prefix}'")
    print(f"  Expected color: {expected_style}")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

print("\n" + "=" * 50)
print("All tests done")
print("=" * 50)