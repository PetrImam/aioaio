from aiohttp import web
import aiosqlite
from db import DB_NAME
from auth import hash_password, check_password, create_token


# ---------------- USERS ----------------

async def create_user(request):
    data = await request.json()

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (data["username"], hash_password(data["password"]), data.get("role", "user"))
        )
        await db.commit()

    return web.json_response({"status": "created"})


async def get_user(request):
    user_id = request.match_info["user_id"]

    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = await cur.fetchone()

    return web.json_response({"user": user})


# ---------------- LOGIN ----------------

async def login(request):
    data = await request.json()

    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute(
            "SELECT * FROM users WHERE username=?",
            (data["username"],)
        )
        user = await cur.fetchone()

    if not user or not check_password(data["password"], user[2]):
        return web.json_response({"error": "invalid credentials"}, status=401)

    token = create_token(user[0])

    return web.json_response({"token": token})


# ---------------- ADS ----------------

async def create_ad(request):
    if not request.user:
        return web.json_response({"error": "unauthorized"}, status=401)

    data = await request.json()

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "INSERT INTO ads (title, description, price, user_id) VALUES (?, ?, ?, ?)",
            (data["title"], data["description"], data["price"], request.user["user_id"])
        )
        await db.commit()

    return web.json_response({"status": "created"})


async def get_ad(request):
    ad_id = request.match_info["ad_id"]

    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT * FROM ads WHERE id=?", (ad_id,))
        ad = await cur.fetchone()

    if not ad:
        return web.json_response({"error": "not found"}, status=404)

    return web.json_response({"ad": ad})


async def delete_ad(request):
    if not request.user:
        return web.json_response({"error": "unauthorized"}, status=401)

    ad_id = request.match_info["ad_id"]

    async with aiosqlite.connect(DB_NAME) as db:
        cur = await db.execute("SELECT user_id FROM ads WHERE id=?", (ad_id,))
        ad = await cur.fetchone()

        if not ad:
            return web.json_response({"error": "not found"}, status=404)

        if request.user["role"] != "admin" and ad[0] != request.user["user_id"]:
            return web.json_response({"error": "forbidden"}, status=403)

        await db.execute("DELETE FROM ads WHERE id=?", (ad_id,))
        await db.commit()

    return web.json_response({"status": "deleted"})


async def search_ads(request):
    title = request.query.get("title")

    async with aiosqlite.connect(DB_NAME) as db:
        if title:
            cur = await db.execute("SELECT * FROM ads WHERE title LIKE ?", (f"%{title}%",))
        else:
            cur = await db.execute("SELECT * FROM ads")

        ads = await cur.fetchall()

    return web.json_response({"ads": ads})