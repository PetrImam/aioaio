from aiohttp import web
from auth import decode_token


@web.middleware
async def auth_middleware(request, handler):
    request.user = None

    token = request.headers.get("Authorization")

    if token and token.startswith("Bearer "):
        token = token.split(" ")[1]
        payload = decode_token(token)

        if payload:
            request.user = payload

    return await handler(request)