from aiohttp import web
from models import Advertisement
from database import SessionLocal
from utils import get_current_user


async def create_ad(request):

    user = await get_current_user(request)

    data = await request.json()

    async with SessionLocal() as session:

        ad = Advertisement(
            title=data["title"],
            description=data["description"],
            price=data["price"],
            user_id=user.id
        )

        session.add(ad)

        await session.commit()

        return web.json_response({"id": ad.id}, status=201)


async def get_ad(request):

    ad_id = int(request.match_info["ad_id"])

    async with SessionLocal() as session:

        ad = await session.get(Advertisement, ad_id)

        if not ad:

            return web.json_response({"error": "not found"}, status=404)

        return web.json_response({
            "id": ad.id,
            "title": ad.title,
            "description": ad.description,
            "price": ad.price
        })


async def delete_ad(request):

    user = await get_current_user(request)

    ad_id = int(request.match_info["ad_id"])

    async with SessionLocal() as session:

        ad = await session.get(Advertisement, ad_id)

        if not ad:

            return web.json_response({"error": "not found"}, status=404)

        if user.role != "admin" and ad.user_id != user.id:

            raise web.HTTPForbidden()

        await session.delete(ad)

        await session.commit()

        return web.Response(status=204)