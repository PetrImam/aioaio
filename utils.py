from aiohttp import web
from auth import decode_token
from models import User
from database import SessionLocal


async def get_current_user(request):

    auth = request.headers.get("Authorization")

    if not auth:

        raise web.HTTPUnauthorized()

    token = auth.replace("Bearer ", "")

    payload = decode_token(token)

    if not payload:

        raise web.HTTPUnauthorized()

    async with SessionLocal() as session:

        user = await session.get(User, payload["user_id"])

        if not user:

            raise web.HTTPUnauthorized()

        return user