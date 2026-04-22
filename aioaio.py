# app.py

from aiohttp import web
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    create_engine,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import json

# -----------------------------
# DATABASE
# -----------------------------

DATABASE_URL = "sqlite:///ads.db"

engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)

Base = declarative_base()


# -----------------------------
# MODEL
# -----------------------------

class Advertisement(Base):
    __tablename__ = "advertisements"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = Column(String(100), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "owner": self.owner,
        }


Base.metadata.create_all(engine)


# -----------------------------
# HELPERS
# -----------------------------

async def get_json(request):
    try:
        return await request.json()
    except json.JSONDecodeError:
        return None


# -----------------------------
# CREATE AD
# POST /ads
# -----------------------------

async def create_ad(request):
    data = await get_json(request)

    if not data:
        return web.json_response(
            {"error": "Invalid JSON"},
            status=400
        )

    if "title" not in data or "description" not in data:
        return web.json_response(
            {"error": "title and description required"},
            status=400
        )

    session = Session()

    try:
        ad = Advertisement(
            title=data["title"],
            description=data["description"],
            owner=data.get("owner", "anonymous")
        )

        session.add(ad)
        session.commit()

        return web.json_response(
            ad.to_dict(),
            status=201
        )

    except Exception as e:
        session.rollback()

        return web.json_response(
            {"error": str(e)},
            status=500
        )

    finally:
        session.close()


# -----------------------------
# GET ONE AD
# GET /ads/{ad_id}
# -----------------------------

async def get_ad(request):
    ad_id = request.match_info["ad_id"]

    session = Session()

    try:
        ad = session.get(Advertisement, int(ad_id))

        if not ad:
            return web.json_response(
                {"error": "Ad not found"},
                status=404
            )

        return web.json_response(ad.to_dict())

    finally:
        session.close()


# -----------------------------
# GET ALL ADS
# GET /ads
# -----------------------------

async def list_ads(request):
    session = Session()

    try:
        ads = session.query(Advertisement).all()

        return web.json_response([
            ad.to_dict() for ad in ads
        ])

    finally:
        session.close()


# -----------------------------
# UPDATE AD
# PUT /ads/{ad_id}
# -----------------------------

async def update_ad(request):
    ad_id = request.match_info["ad_id"]

    data = await get_json(request)

    if not data:
        return web.json_response(
            {"error": "Invalid JSON"},
            status=400
        )

    session = Session()

    try:
        ad = session.get(Advertisement, int(ad_id))

        if not ad:
            return web.json_response(
                {"error": "Ad not found"},
                status=404
            )

        if "title" in data:
            ad.title = data["title"]

        if "description" in data:
            ad.description = data["description"]

        if "owner" in data:
            ad.owner = data["owner"]

        session.commit()

        return web.json_response(ad.to_dict())

    except Exception as e:
        session.rollback()

        return web.json_response(
            {"error": str(e)},
            status=500
        )

    finally:
        session.close()


# -----------------------------
# DELETE AD
# DELETE /ads/{ad_id}
# -----------------------------

async def delete_ad(request):
    ad_id = request.match_info["ad_id"]

    session = Session()

    try:
        ad = session.get(Advertisement, int(ad_id))

        if not ad:
            return web.json_response(
                {"error": "Ad not found"},
                status=404
            )

        session.delete(ad)
        session.commit()

        return web.Response(status=204)

    except Exception as e:
        session.rollback()

        return web.json_response(
            {"error": str(e)},
            status=500
        )

    finally:
        session.close()


# -----------------------------
# APP
# -----------------------------

app = web.Application()

app.router.add_post("/ads", create_ad)
app.router.add_get("/ads", list_ads)
app.router.add_get("/ads/{ad_id}", get_ad)
app.router.add_put("/ads/{ad_id}", update_ad)
app.router.add_delete("/ads/{ad_id}", delete_ad)


if __name__ == "__main__":
    web.run_app(app, host="127.0.0.1", port=8080)