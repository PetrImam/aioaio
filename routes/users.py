from aiohttp import web
from models import User
from database import SessionLocal
from auth import hash_password


async def register(request):

    data = await request.json()

    async with SessionLocal() as session:

        user = User(
            username=data["username"],
            password_hash=hash_password(data["password"]),
            role="user"
        )

        session.add(user)

        await session.commit()

        return web.json_response({"status": "created"}, status=201)