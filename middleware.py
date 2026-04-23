from aiohttp import web
from auth import decode_token


@web.middleware
async def auth_middleware(request, handler):

    request["user"] = None

    auth_header = request.headers.get("Authorization")

    if auth_header and auth_header.startswith("Bearer "):

        token = auth_header.split(" ")[1]

        payload = decode_token(token)

        if payload:
            request["user"] = payload

    return await handler(request)