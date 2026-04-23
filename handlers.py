from aiohttp import web
import aiosqlite

from db import DB_NAME
from auth import (
    hash_password,
    verify_password,
    create_token
)


# ---------------- REGISTER ----------------

async def register(request):

    try:
        data = await request.json()
    except:
        return web.json_response(
            {"error": "Invalid JSON"},
            status=400
        )

    required = ["username", "password"]

    for field in required:
        if field not in data:
            return web.json_response(
                {"error": f"{field} required"},
                status=400
            )

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT id FROM users WHERE username=?",
            (data["username"],)
        )

        exists = await cursor.fetchone()

        if exists:
            return web.json_response(
                {"error": "User exists"},
                status=400
            )

        await db.execute(
            """
            INSERT INTO users
            (username, password_hash, role)
            VALUES (?, ?, ?)
            """,
            (
                data["username"],
                hash_password(data["password"]),
                "user"
            )
        )

        await db.commit()

    return web.json_response(
        {"status": "created"},
        status=201
    )


# ---------------- LOGIN ----------------

async def login(request):

    try:
        data = await request.json()
    except:
        return web.json_response(
            {"error": "Invalid JSON"},
            status=400
        )

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT id, password_hash, role
            FROM users
            WHERE username=?
            """,
            (data["username"],)
        )

        user = await cursor.fetchone()

    if not user:
        return web.json_response(
            {"error": "Invalid credentials"},
            status=401
        )

    if not verify_password(data["password"], user[1]):
        return web.json_response(
            {"error": "Invalid credentials"},
            status=401
        )

    token = create_token(
        user[0],
        user[2]
    )

    return web.json_response({
        "token": token
    })


# ---------------- CREATE AD ----------------

async def create_ad(request):

    user = request["user"]

    if not user:
        return web.json_response(
            {"error": "Unauthorized"},
            status=401
        )

    try:
        data = await request.json()
    except:
        return web.json_response(
            {"error": "Invalid JSON"},
            status=400
        )

    required = [
        "title",
        "description",
        "price"
    ]

    for field in required:
        if field not in data:
            return web.json_response(
                {"error": f"{field} required"},
                status=400
            )

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            INSERT INTO advertisements
            (title, description, price, user_id)
            VALUES (?, ?, ?, ?)
            """,
            (
                data["title"],
                data["description"],
                data["price"],
                user["user_id"]
            )
        )

        await db.commit()

        ad_id = cursor.lastrowid

    return web.json_response({
        "id": ad_id
    }, status=201)


# ---------------- GET AD ----------------

async def get_ad(request):

    try:
        ad_id = int(
            request.match_info["ad_id"]
        )

    except:
        return web.json_response(
            {"error": "Invalid id"},
            status=400
        )

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT id, title, description,
                   price, user_id
            FROM advertisements
            WHERE id=?
            """,
            (ad_id,)
        )

        ad = await cursor.fetchone()

    if not ad:
        return web.json_response(
            {"error": "Not found"},
            status=404
        )

    return web.json_response({
        "id": ad[0],
        "title": ad[1],
        "description": ad[2],
        "price": ad[3],
        "user_id": ad[4]
    })


# ---------------- DELETE AD ----------------

async def delete_ad(request):

    user = request["user"]

    if not user:
        return web.json_response(
            {"error": "Unauthorized"},
            status=401
        )

    ad_id = int(request.match_info["ad_id"])

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT user_id
            FROM advertisements
            WHERE id=?
            """,
            (ad_id,)
        )

        ad = await cursor.fetchone()

        if not ad:
            return web.json_response(
                {"error": "Not found"},
                status=404
            )

        owner_id = ad[0]

        if (
            user["role"] != "admin"
            and owner_id != user["user_id"]
        ):
            return web.json_response(
                {"error": "Forbidden"},
                status=403
            )

        await db.execute(
            "DELETE FROM advertisements WHERE id=?",
            (ad_id,)
        )

        await db.commit()

    return web.Response(status=204)