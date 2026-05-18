import csv, sqlite3

conn = sqlite3.connect("ROUTES.db")
cursor = conn.cursor()

with open('cracker.csv','r') as csvdata:
    all = csv.DictReader(csvdata)
    to_db = [(row['PREFIX'], row['SERIES_NAME'], row['TO_WEB'], row['TO_VOS'], row['TO_NEXIO'], row['TO_AFFILIATE'], row['TO_TMD'], row['WEB_PATH']) for row in all]

cursor.executemany("INSERT INTO routes (prefix, series, to_web, to_vos, to_nexio, to_affiliate, to_tmd, web_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db)
conn.commit()
conn.close()