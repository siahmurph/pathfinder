import sqlite3
 
conn = sqlite3.connect('ROUTES.db')
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS routes")
 
create_table = '''CREATE TABLE IF NOT EXISTS routes(
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL UNIQUE,
                prefix VARCHAR(16) NOT NULL UNIQUE,
                series VARCHAR(256) NULL,
                to_web VARCHAR(8) NULL,
                to_vos VARCHAR(8) NULL,
                to_nexio VARCHAR(8) NULL,
                to_affiliate VARCHAR(8) NULL,
                to_tmd VARCHAR(8) NULL,
                web_path VARCHAR(512) NULL);
                '''

cursor.execute(create_table)
conn.commit()
conn.close()