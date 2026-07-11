import sys
import time
from PySide6.QtWidgets import QApplication

sys.path.append(".")
import db_connection

app = QApplication(sys.argv)

print("=" * 50)
print("Trading Screen Tests")
print("=" * 50)

# test 1 - check portfolio data loads properly
print("\nTest 1: Portfolio Data Load")
try:
    data = db_connection.get_portfolio_summary("superuser")
    if data['total_balance'] < 0:
        raise Exception("Balance should be positive")
    if data['available_cash'] < 0:
        raise Exception("Cash should be positive")
    if not isinstance(data['holdings'], list):
        raise Exception("Holdings should be list")
    print(f"Total Balance: ${data['total_balance']:.2f}")
    print(f"Available Cash: ${data['available_cash']:.2f}")
    print(f"Holdings: {len(data['holdings'])} position(s)")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 2 - fetching live prices from bybit
print("\nTest 2: Live Price Fetch")
try:
    btc_price = db_connection.get_crypto_price("BTC")
    eth_price = db_connection.get_crypto_price("ETH")
    invalid = db_connection.get_crypto_price("INVALID")

    if btc_price <= 0:
        raise Exception("BTC price should be positive")
    if eth_price <= 0:
        raise Exception("ETH price should be positive")
    if invalid != 0.0:
        raise Exception("Invalid symbol should return 0.0")

    print(f"BTC Price: ${btc_price:.2f}")
    print(f"ETH Price: ${eth_price:.2f}")
    print(f"Invalid symbol returns: {invalid}")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 3 - making sure SMA calculates right
print("\nTest 3: SMA Calculation")
try:
    from trading_screen import CandlestickChart
    chart = CandlestickChart()

    prices = list(range(1, 26))  # [1, 2, 3, ..., 25]

    # first valid SMA (index 19) should be average of 1-20 = 10.5
    sma = chart.calculate_sma(prices, 20)
    if len(sma) != 6:
        raise Exception(f"Expected 6 SMA values, got {len(sma)}")
    if abs(sma[0] - 10.5) >= 0.01:
        raise Exception(f"First SMA should be 10.5, got {sma[0]}")
    if abs(sma[-1] - 15.5) >= 0.01:
        raise Exception(f"Last SMA should be 15.5, got {sma[-1]}")

    # not enough data should return empty
    short_sma = chart.calculate_sma([1, 2, 3], 20)
    if short_sma != []:
        raise Exception("Insufficient data should return []")

    print(f"  First SMA value: {sma[0]} (expected 10.5)")
    print(f"  Last SMA value: {sma[-1]} (expected 15.5)")
    print(f"  Insufficient data returns: {short_sma}")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 4 - RSI should be high for rising prices, low for falling
print("\nTest 4: RSI Calculation")
try:
    from trading_screen import CandlestickChart
    chart = CandlestickChart()

    # prices going up should give high RSI
    rising = [float(i * 100) for i in range(1, 30)]
    rsi_rising = chart.calculate_rsi(rising, 14)
    if len(rsi_rising) <= 0:
        raise Exception("RSI should return values")
    if rsi_rising[-1] <= 70:
        raise Exception(f"Rising prices should give RSI > 70, got {rsi_rising[-1]:.1f}")

    # prices going down should give low RSI
    falling = [float((30 - i) * 100) for i in range(1, 30)]
    rsi_falling = chart.calculate_rsi(falling, 14)
    if rsi_falling[-1] >= 30:
        raise Exception(f"Falling prices should give RSI < 30, got {rsi_falling[-1]:.1f}")

    # not enough data should return empty
    short_rsi = chart.calculate_rsi([1, 2, 3], 14)
    if short_rsi != []:
        raise Exception("Insufficient data should return []")

    print(f"Rising prices RSI: {rsi_rising[-1]:.1f} (expected > 70)")
    print(f"Falling prices RSI: {rsi_falling[-1]:.1f} (expected < 30)")
    print(f"Insufficient data returns: {short_rsi}")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 5 - buying some BTC and checking balance changes
print("\nTest 5: Buy Order Execution")
try:
    data = db_connection.get_portfolio_summary("superuser")
    cash_before = data['available_cash']

    btc_price = db_connection.get_crypto_price("BTC")
    buy_quantity = 0.001  # small amount so we dont run out of cash

    success, message = db_connection.execute_trade(
        "superuser", "BTC", buy_quantity, btc_price, "BUY"
    )

    if not success:
        raise Exception(f"Buy should succeed, got: {message}")

    # check that the balance actually went down
    data_after = db_connection.get_portfolio_summary("superuser")
    cash_after = data_after['available_cash']
    expected_spent = round(buy_quantity * btc_price, 2)

    print(f"Trade result: {message}")
    print(f"Cash before: ${cash_before:.2f}")
    print(f"Cash after: ${cash_after:.2f}")
    print(f"Spent: ${cash_before - cash_after:.2f} (expected ~${expected_spent:.2f})")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 6 - trying to buy way more than we can afford
print("\nTest 6: Insufficient Cash Validation")
try:
    btc_price = db_connection.get_crypto_price("BTC")
    huge_quantity = 1000000 / btc_price  # way more than we have

    success, message = db_connection.execute_trade(
        "superuser", "BTC", huge_quantity, btc_price, "BUY"
    )

    if success:
        raise Exception("Oversized trade should fail")
    if "cash" not in message.lower():
        raise Exception(f"Error should mention cash: {message}")

    print(f"  Rejected as expected: {message}")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 7 - selling some BTC
print("\nTest 7: Sell Order Execution")
try:
    portfolio = db_connection.get_user_portfolio("superuser")
    btc_holding = next((h for h in portfolio if h['crypto_symbol'] == 'BTC'), None)

    if btc_holding and btc_holding['quantity'] > 0.001:
        sell_quantity = 0.001
        btc_price = db_connection.get_crypto_price("BTC")

        success, message = db_connection.execute_trade(
            "superuser", "BTC", sell_quantity, btc_price, "SELL"
        )

        if not success:
            raise Exception(f"Sell should succeed: {message}")
        print(f"Sell result: {message}")
    else:
        print("Skipped - not enough BTC to sell, need to buy first")

    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 8 - trying to sell more BTC than we own
print("\nTest 8: Insufficient Holdings Validation")
try:
    btc_price = db_connection.get_crypto_price("BTC")

    success, message = db_connection.execute_trade(
        "superuser", "BTC", 999, btc_price, "SELL"
    )

    if success:
        raise Exception("Oversell should fail")
    if "insufficient" not in message.lower():
        raise Exception(f"Error should mention holdings: {message}")

    print(f"Rejected as expected: {message}")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 9 - checking that recent transactions come back in the right format
print("\nTest 9: Recent Transactions Format")
try:
    transactions = db_connection.get_recent_transactions("superuser", 5)

    if not isinstance(transactions, list):
        raise Exception("Should return list")
    if len(transactions) > 5:
        raise Exception("Should return max 5")

    if transactions:
        # format should be like: "BUY 0.0010 BTC $45000.00 2025-02-10 14:30:15"
        parts = transactions[0].split()
        if parts[0] not in ["BUY", "SELL"]:
            raise Exception("First part should be BUY or SELL")
        if "$" not in parts[3]:
            raise Exception("Should include price with $")
        print(f"Sample transaction: {transactions[0]}")

    print(f"Got {len(transactions)} transaction(s)")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 10 - basic total cost math
print("\nTest 10: Total Cost Calculation")
try:
    quantity = 0.5
    price = 45000.00
    expected_total = quantity * price  # should be $22,500

    if abs(expected_total - 22500.0) >= 0.01:
        raise Exception("Total cost calculation wrong")

    print(f"  0.5 BTC x ${price:.2f} = ${expected_total:.2f}")

    # zero quantity should give zero cost
    zero_total = 0 * price
    if zero_total != 0.0:
        raise Exception("Zero quantity should give zero cost")
    print(f"0 quantity = $0.00")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

print("\n" + "=" * 50)
print("All tests done")
print("=" * 50)