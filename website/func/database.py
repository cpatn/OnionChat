import aiosqlite
from contextlib import asynccontextmanager
import datetime
import json

@asynccontextmanager
async def getdb():
    conn = await aiosqlite.connect('website/db/database.db')
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA foreign_keys=ON")
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA synchronous=NORMAL")
    await conn.execute("PRAGMA temp_store=MEMORY")
    try:
        yield conn
    finally:
        await conn.close()

async def dataTable():
    async with getdb() as conn:
        await conn.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            displayname TEXT DEFAULT NULL,
            password TEXT NOT NULL,
            avatar TEXT DEFAULT 'default.webp',
            flags TEXT DEFAULT 'user',
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP                 
        )""")
        await conn.commit()

async def addUser(username, password):
    async with getdb() as conn:
        cursor = await conn.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", (username, password))
        await conn.commit()
        if cursor.rowcount == 1:
            return cursor.lastrowid
        return None
    
async def loginUser(username, password):
    async with getdb() as conn:
        async with conn.execute("SELECT * FROM users WHERE username = ?", (username,)) as cursor:
            data = await cursor.fetchone()
        if not data:
            return {"status": "user_not_found"}
        if data["password"] != password:
            return {"status": "wrong_password"}
        return {"status": "success", "user": dict(data)}
