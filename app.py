import json
from typing import Any

from aiohttp import web
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from models import Advertisement, Base

# ---------------------------------------------------------------------------
# Настройка БД
# ---------------------------------------------------------------------------
DATABASE_URL = "sqlite+aiosqlite:///ads.db"

engine = create_async_engine(DATABASE_URL, echo=False)
Session = async_sessionmaker(engine, expire_on_commit=False)


# ---------------------------------------------------------------------------
# Вспомогательные функции
# ---------------------------------------------------------------------------
def json_response(data: Any, status: int = 200) -> web.Response:
    return web.Response(
        text=json.dumps(data, ensure_ascii=False),
        status=status,
        content_type="application/json",
    )


async def get_ad_or_404(session: AsyncSession, ad_id: int) -> Advertisement:
    ad = await session.get(Advertisement, ad_id)
    if ad is None:
        raise web.HTTPNotFound(
            text=json.dumps({"error": "Объявление не найдено"}),
            content_type="application/json",
        )
    return ad


# ---------------------------------------------------------------------------
# Обработчики
# ---------------------------------------------------------------------------
class AdvertisementView(web.View):
    """
    POST   /api/ads          — создать объявление
    GET    /api/ads          — список всех объявлений
    GET    /api/ads/{id}     — получить объявление
    PUT    /api/ads/{id}     — обновить объявление
    DELETE /api/ads/{id}     — удалить объявление
    """

    # -----------------------------------------------------------------------
    # POST /api/ads
    # -----------------------------------------------------------------------
    async def post(self) -> web.Response:
        data = await self.request.json()

        if "title" not in data or "description" not in data:
            raise web.HTTPBadRequest(
                text=json.dumps({"error": "Поля title и description обязательны"}),
                content_type="application/json",
            )

        async with Session() as session:
            try:
                ad = Advertisement(
                    title=data["title"],
                    description=data["description"],
                    owner=data.get("owner", "anonymous"),
                )
                session.add(ad)
                await session.commit()
                await session.refresh(ad)
                return json_response(ad.to_dict(), status=201)
            except SQLAlchemyError as e:
                await session.rollback()
                raise web.HTTPInternalServerError(
                    text=json.dumps({"error": str(e)}),
                    content_type="application/json",
                )

    # -----------------------------------------------------------------------
    # GET /api/ads
    # -----------------------------------------------------------------------
    async def get(self) -> web.Response:
        ad_id = self.request.match_info.get("ad_id")

        async with Session() as session:
            # GET /api/ads/<id>
            if ad_id is not None:
                ad = await get_ad_or_404(session, int(ad_id))
                return json_response(ad.to_dict())

            # GET /api/ads
            result = await session.execute(select(Advertisement))
            ads = result.scalars().all()
            return json_response([ad.to_dict() for ad in ads])

    # -----------------------------------------------------------------------
    # PUT /api/ads/<id>
    # -----------------------------------------------------------------------
    async def put(self) -> web.Response:
        ad_id = int(self.request.match_info["ad_id"])
        data = await self.request.json()

        async with Session() as session:
            ad = await get_ad_or_404(session, ad_id)
            try:
                for field in ("title", "description", "owner"):
                    if field in data:
                        setattr(ad, field, data[field])
                await session.commit()
                await session.refresh(ad)
                return json_response(ad.to_dict())
            except SQLAlchemyError as e:
                await session.rollback()
                raise web.HTTPInternalServerError(
                    text=json.dumps({"error": str(e)}),
                    content_type="application/json",
                )

    # -----------------------------------------------------------------------
    # DELETE /api/ads/<id>
    # -----------------------------------------------------------------------
    async def delete(self) -> web.Response:
        ad_id = int(self.request.match_info["ad_id"])

        async with Session() as session:
            ad = await get_ad_or_404(session, ad_id)
            try:
                await session.delete(ad)
                await session.commit()
                return web.Response(status=204)
            except SQLAlchemyError as e:
                await session.rollback()
                raise web.HTTPInternalServerError(
                    text=json.dumps({"error": str(e)}),
                    content_type="application/json",
                )


# ---------------------------------------------------------------------------
# Инициализация БД при старте
# ---------------------------------------------------------------------------
async def on_startup(app: web.Application) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def on_cleanup(app: web.Application) -> None:
    await engine.dispose()


# ---------------------------------------------------------------------------
# Фабрика приложения
# ---------------------------------------------------------------------------
def create_app() -> web.Application:
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    app.router.add_route("*", "/api/ads", AdvertisementView)
    app.router.add_route("*", "/api/ads/{ad_id:\\d+}", AdvertisementView)

    return app


if __name__ == "__main__":
    web.run_app(create_app(), host="0.0.0.0", port=8080)
