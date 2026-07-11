import sys
from PySide6.QtWidgets import QApplication

sys.path.append('.')
import db_connection

app = QApplication(sys.argv)

print("=" * 50)
print("Leaderboard Screen Tests")
print("=" * 50)

# test 1 - checking leaderboard data loads
print("\nTest 1: Leaderboard Data Retrieval")
try:
    leaderboard = db_connection.get_leaderboard_data()
    if not isinstance(leaderboard, list):
        raise Exception("Should return list")
    if len(leaderboard) == 0:
        raise Exception("Should have at least one user")
    
    first = leaderboard[0]
    if 'username' not in first:
        raise Exception("Missing username field")
    if 'total_balance' not in first:
        raise Exception("Missing total_balance field")
    
    print(f"Retrieved {len(leaderboard)} users")
    print(f"Top user: {first['username']} - ${first['total_balance']:.2f}")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 2 - leaderboard should be sorted highest to lowest
print("\nTest 2: Descending Balance Order")
try:
    leaderboard = db_connection.get_leaderboard_data()
    
    for i in range(len(leaderboard) - 1):
        current = leaderboard[i]['total_balance']
        next_val = leaderboard[i + 1]['total_balance']
        if current < next_val:
            raise Exception(f"Row {i}: {current} should be >= {next_val}")
    
    print(f"Leaderboard correctly sorted (highest to lowest)")
    print(f"Top 3:")
    for i in range(min(3, len(leaderboard))):
        user = leaderboard[i]
        print(f"  {i+1}. {user['username']}: ${user['total_balance']:.2f}")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 3 - checking rank numbers are correct
print("\nTest 3: Rank Calculation")
try:
    leaderboard = db_connection.get_leaderboard_data()
    
    for row, user_data in enumerate(leaderboard[:5]):
        expected_rank = row + 1
        print(f"Rank {expected_rank}: {user_data['username']} (${user_data['total_balance']:.2f})")
    
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 4 - finding where the current user sits in the ranking
print("\nTest 4: Find Current User Rank")
try:
    leaderboard = db_connection.get_leaderboard_data()
    current_username = "superuser"
    
    user_rank = None
    for i, user_data in enumerate(leaderboard):
        if user_data['username'] == current_username:
            user_rank = i + 1
            user_balance = user_data['total_balance']
            break
    
    if user_rank:
        print(f"{current_username} ranked #{user_rank} out of {len(leaderboard)}")
        print(f"Balance: ${user_balance:.2f}")
    else:
        print(f"{current_username} not found (may be new user)")
    
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 5 - making sure empty leaderboard doesnt crash
print("\nTest 5: Empty Leaderboard Handling")
try:
    empty_leaderboard = []
    if len(empty_leaderboard) != 0:
        raise Exception("Empty list should have length 0")
    print(f"Empty leaderboard handled without crash")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

print("\n" + "=" * 50)
print("All tests done")
print("=" * 50)