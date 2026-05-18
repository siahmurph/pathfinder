import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
from pydantic import BaseModel

# 1. Initialize the App
# Gets ROOT_PATH from docker-compose.yml (e.g., "/api") or defaults to ""
app_root_path = os.getenv("ROOT_PATH", "")
app = FastAPI(root_path=app_root_path)

# 2. CORS Settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Database Connection
def create_connection():
    # In Docker, this will be "/app/data/ROUTES.db"
    # Locally, it will look for "ROUTES.db" in your current folder
    db_path = os.getenv("DB_PATH", "ROUTES.db")
    connection = sqlite3.connect(db_path)
    return connection

# ... rest of your routes (Post, add_one, get_all, etc.) stay exactly as they are ...
#original Lines
# def create_connection():
#     connection = sqlite3.connect("ROUTES.db")
#     return connection

@app.get("/")
def test_connection():
    return {"message": "Welcome"}

class Post(BaseModel):
    prefix: str
    program: str
    folderPath: str
    locations: list

@app.post("/items", status_code=201)
def add_one(entry: Post):
    to_web = "YES" if "toWeb" in entry.locations else "NO"
    to_vos = "YES" if "toVOS" in entry.locations else "NO"
    to_nexio = "YES" if "toNexio" in entry.locations else "NO"
    to_affiliate = "YES" if "toAffiliate" in entry.locations else "NO"
    to_tmd = "YES" if "toTMD" in entry.locations else "NO"
    conn = create_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        c = cursor.execute("INSERT INTO routes (prefix, series, to_web, to_vos, to_nexio, to_affiliate, to_tmd, web_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?) returning *", (entry.prefix, entry.program, to_web, to_vos, to_nexio, to_affiliate, to_tmd, entry.folderPath,)).fetchone()
        conn.commit()
        conn.close()
        # return {"message": "good"}
        return c
    except sqlite3.Error as er:
        conn.close()
        return {"message": ' '.join(er.args)}

@app.get("/items")
def get_all():
    conn = create_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM routes")
    data = cursor.fetchall()
    conn.commit()
    conn.close()
    return data if data else {"message": "empty"}

@app.get("/items/{prefix}")
def get_one(prefix):
    conn = create_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM routes WHERE prefix = ?", (prefix.upper(),))
    data = cursor.fetchone()
    conn.commit()
    conn.close()
    return data if data else {"message": "empty"}

class Put(BaseModel):
    id: int
    prefix: str
    program: str
    folderPath: str
    locations: list

@app.put("/items")
def update_one(entry: Put):
    to_web = "YES" if "toWeb" in entry.locations else "NO"
    to_vos = "YES" if "toVOS" in entry.locations else "NO"
    to_nexio = "YES" if "toNexio" in entry.locations else "NO"
    to_affiliate = "YES" if "toAffiliate" in entry.locations else "NO"
    to_tmd = "YES" if "toTMD" in entry.locations else "NO"
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE routes SET prefix = ?, series = ?, to_web = ?, to_vos = ?, to_nexio = ?, to_affiliate = ?, to_tmd = ?, web_path = ? WHERE id = ?", (entry.prefix, entry.program, to_web, to_vos, to_nexio, to_affiliate, to_tmd, entry.folderPath, entry.id,))
    conn.commit()
    conn.close()
    return {"message": "good"}

@app.delete("/items/{id}")
def remove_one(id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM routes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return {"message": "good"}
