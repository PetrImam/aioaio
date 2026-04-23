from aiohttp import web
from database import engine, Base

from routes.users import register
from routes.ads import create_ad, get_ad, delete_ad


async def init_db():

    async with engine.begin() as conn:

        await conn.run_sync(Base.metadata.create_all)


app = web.Application()

app.router.add_post("/user", register)

app.router.add_post("/ads", create_ad)

app.router.add_get("/ads/{ad_id}", get_ad)

app.router.add_delete("/ads/{ad_id}", delete_ad)


if __name__ == "__main__":

    web.run_app(app, port=8080)