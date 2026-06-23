import csv
import os
import sqlite3


seed_paths = ["seed.csv", "seed.txt", "routing_rules.csv"]
seed_path = next((path for path in seed_paths if os.path.exists(path)), None)

if seed_path:
    conn = sqlite3.connect("pathfinder.db")
    cursor = conn.cursor()

    with open(seed_path, "r", newline="") as csvdata:
        rows = csv.DictReader(csvdata)
        to_db = [
            (
                row.get("program_name") or None,
                row["match_type"],
                row["pattern"],
                row.get("min_duration_sec") or None,
                row.get("max_duration_sec") or None,
                row["destination_1"],
                row.get("destination_2") or None,
                int(row.get("promo_possible") or 0),
            )
            for row in rows
        ]

    cursor.executemany(
        "INSERT INTO routing_rules (program_name, match_type, pattern, min_duration_sec, max_duration_sec, destination_1, destination_2, promo_possible) VALUES (?, ?, ?, ?, ?, ?, ?, ?);",
        to_db,
    )
    conn.commit()
    conn.close()