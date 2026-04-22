from aiohttp import web
from db import init_db
from handlers import *
from middleware import auth_middleware


app = web.Application(middlewares=[auth_middleware])


# USERS
app.router.add_post("/user", create_user)
app.router.add_get("/user/{user_id}", get_user)

# LOGIN
app.router.add_post("/login", login)

# ADS
app.router.add_post("/advertisement", create_ad)
app.router.add_get("/advertisement/{ad_id}", get_ad)
app.router.add_delete("/advertisement/{ad_id}", delete_ad)
app.router.add_get("/advertisement", search_ads)


async def on_startup(app):
    await init_db()


app.on_startup.append(on_startup)

web.run_app(app, port=8080)