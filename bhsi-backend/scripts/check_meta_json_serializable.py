import sqlite3
import json

DB_PATH = 'app/db/queue.db'  # Adjust path if needed


def is_json_serializable(value):
    try:
        json.dumps(value)
        return True
    except (TypeError, OverflowError):
        return False


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT rowid, meta FROM raw_docs")
    rows = cursor.fetchall()
    non_serializable = []
    for rowid, meta_str in rows:
        try:
            # Try to load as JSON if it's a string
            meta = json.loads(meta_str) if isinstance(meta_str, str) else meta_str
            json.dumps(meta)
        except Exception as e:
            print(f"Row {rowid} not serializable: {e}\n  meta: {meta_str}")
            non_serializable.append(rowid)
    print(f"\nChecked {len(rows)} rows. "
          f"{len(non_serializable)} not serializable.")
    if non_serializable:
        print(f"Non-serializable rowids: {non_serializable}")
    else:
        print("All meta values are JSON-serializable!")


if __name__ == "__main__":
    main() 