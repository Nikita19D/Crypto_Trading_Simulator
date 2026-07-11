from PySide6.QtWidgets import QApplication

import sys
sys.path.append(".")
from learning import LearningScreen

app = QApplication(sys.argv)

print("=" * 50)
print("Learning Screen Tests")
print("=" * 50)

# test 1 - module content displays correctly
print("\nTest 1: Content Display")
try:
    learning = LearningScreen("superuser")
    learning.show_module_content(1)

    if learning.content_title.text() != "Getting Started with Crypto Trading":
        raise Exception(f"Wrong title: {learning.content_title.text()}")
    if len(learning.content_text.text()) <= 300:
        raise Exception(f"Content too short: {len(learning.content_text.text())} chars")

    print(f"Title: {learning.content_title.text()}")
    print(f"Content length: {len(learning.content_text.text())} chars")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 2 - progress tracking updates correctly
print("\nTest 2: Progress Tracking")
try:
    learning = LearningScreen("superuser")

    learning.show_module_content(1)
    if learning.visited_modules != {1}:
        raise Exception(f"Visited should be {{1}}, got {learning.visited_modules}")
    if learning.progress_bar.value() != 25:
        raise Exception(f"Progress should be 25%, got {learning.progress_bar.value()}%")

    learning.show_module_content(2)
    if learning.visited_modules != {1, 2}:
        raise Exception(f"Visited should be {{1, 2}}, got {learning.visited_modules}")
    if learning.progress_bar.value() != 50:
        raise Exception(f"Progress should be 50%, got {learning.progress_bar.value()}%")

    # revisit module 1 - should not change progress
    learning.show_module_content(1)
    if learning.visited_modules != {1, 2}:
        raise Exception(f"Revisit changed visited: {learning.visited_modules}")
    if learning.progress_bar.value() != 50:
        raise Exception(f"Revisit changed progress: {learning.progress_bar.value()}%")

    print(f"After module 1: progress = 25%")
    print(f"After module 2: progress = 50%")
    print(f"Revisit module 1: progress still 50%")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

# test 3 - all modules completion reaches 100%
print("\nTest 3: All Modules Completion")
try:
    learning = LearningScreen("superuser")

    for i in range(1, 5):
        learning.show_module_content(i)

    if len(learning.visited_modules) != 4:
        raise Exception(f"Should have 4 visited, got {len(learning.visited_modules)}")
    if learning.progress_bar.value() != 100:
        raise Exception(f"Progress should be 100%, got {learning.progress_bar.value()}%")

    print(f"Visited modules: {learning.visited_modules}")
    print(f"Progress: {learning.progress_bar.value()}%")
    print("PASSED")
except Exception as e:
    print(f"FAILED: {e}")

print("\n" + "=" * 50)
print("All tests done")
