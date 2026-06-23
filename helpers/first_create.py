import sqlite3


conn = sqlite3.connect("pathfinder.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS routing_rules")

create_table = """CREATE TABLE IF NOT EXISTS routing_rules(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                program_name TEXT,
                match_type TEXT,
                pattern TEXT,
                min_duration_sec INTEGER DEFAULT NULL,
                max_duration_sec INTEGER DEFAULT NULL,
                destination_1 TEXT,
                destination_2 TEXT DEFAULT NULL,
                promo_possible INTEGER DEFAULT 0);
                """

cursor.execute(create_table)
conn.commit()
conn.close()