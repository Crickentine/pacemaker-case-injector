import sqlite3

# Function to get table content
def get_table_content(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name};")
    content = cursor.fetchall()
    conn.close()
    return content

# Paths to the original and updated databases
original_db_path = r"C:\Users\opera\AppData\Roaming\Tonium\Pacemaker\music.db"
updated_db_path = r"C:\Users\opera\AppData\Roaming\Tonium\Pacemaker\music_updated.db"

# Get content of key tables in original and updated databases
original_cases_content = get_table_content(original_db_path, 'cases')
original_tracks_content = get_table_content(original_db_path, 'tracks')
original_casetracks_content = get_table_content(original_db_path, 'casetracks')

updated_cases_content = get_table_content(updated_db_path, 'cases')
updated_tracks_content = get_table_content(updated_db_path, 'tracks')
updated_casetracks_content = get_table_content(updated_db_path, 'casetracks')

# Compare contents and show differences
cases_diff = set(updated_cases_content) - set(original_cases_content)
tracks_diff = set(updated_tracks_content) - set(original_tracks_content)
casetracks_diff = set(updated_casetracks_content) - set(original_casetracks_content)

print("Differences in cases table:")
for diff in cases_diff:
    print(diff)

print("\nDifferences in tracks table:")
for diff in tracks_diff:
    print(diff)

print("\nDifferences in casetracks table:")
for diff in casetracks_diff:
    print(diff)
