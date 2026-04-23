from aiohttp import web

from db import init_db
from handlers import (
    register,
    login,
    create_ad,
    get_ad,
    delete_ad
)

from middleware import auth_middleware


app = web.Application(
    middlewares=[auth_middleware]
)

app.router.add_post("/register", register)
app.router.add_post("/login", login)

app.router.add_post(
    "/advertisement",
    create_ad
)

app.router.add_get(
    "/advertisement/{ad_id}",
    get_ad
)

app.router.add_delete(
    "/advertisement/{ad_id}",
    delete_ad
)


async def startup(app):
    await init_db()


app.on_startup.append(startup)

web.run_app(app, port=8080)