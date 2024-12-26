import sqlite3
import glob
from time import time
import sys

assert len(sys.argv) == 2
task_id = sys.argv[1]
assert len(glob.glob(f"tasks/{task_id}")) > 0, f"task with {task_id} not found"

task_path = f"tasks/{task_id}"

def execute_sql_file(cursor, filename):
    with open(filename, 'r') as file:
        sql_script = file.read()
    cursor.executescript(sql_script)

def fetch_results(cursor, query):
    cursor.execute(query)
    return cursor.fetchall()

def main():
    # Connect to SQLite database (in-memory for testing)
    connection = sqlite3.connect(':memory:')
    cursor = connection.cursor()

    # Step 1: Loop through all test data SQL files
    test_data_files = sorted(glob.glob(f'{task_path}/test_data_*.sql'))  # Adjust the pattern if needed
    for test_data_file in test_data_files:
        print(f"Testcase: {test_data_file} ...", end=' ')

        # Step 2: Execute the before.sql to set up the environment
        execute_sql_file(cursor, f'{task_path}/before.sql')

        # Step 3: Load data from the test data SQL file
        execute_sql_file(cursor, test_data_file)

        # Step 4: Execute and fetch results from answer.sql
        with open(f'{task_path}/answer.sql', 'r') as file:
            answer_query = file.read().strip()
        expected_answer = fetch_results(cursor, answer_query)

        start = time()
        # Step 5: Execute and fetch results from test.sql
        with open('test.sql', 'r') as file:
            test_query = file.read().strip()
        test_results = fetch_results(cursor, test_query)
        end = time()
        # Step 6: Compare results
        # print("Expected Results:", expected_answer)
        # print("Test Results:", test_results)

        print("Passed." if expected_answer == test_results else "Failed.", end=' ')
        print(f"Execute time: {round((end - start)*1000, 3)} seconds")

        # Step 7: Execute the after.sql for any cleanup operations
        execute_sql_file(cursor, f'{task_path}/after.sql')

        print("-" * 40)  # Separator for clarity

    # Close the connection
    connection.close()

if __name__ == '__main__':
    main()