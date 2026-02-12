
import sys
import os

sys.path.append(os.getcwd())

print("Step 1: Script started")

try:
    from src.database.db_connection import init_db
    print("Step 2: Import successful.")
except ImportError as e:
    print(f"Error importing: {e}")
    exit()

if __name__ == "__main__":
    print("Step 3: Running init_db()")
    try:
        init_db()
        print("Step 4: Done!")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
else:
    print("Warning: Script was imported, not run directly.")