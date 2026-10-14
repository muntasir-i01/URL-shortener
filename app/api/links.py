import random
import string
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.link import Link
from app.schemas.link import LinkCreate, LinkMetadata, LinkResponse

from app.cache import redis_client

CACHE_TTL_SECONDS = 3600

router = APIRouter()

BASE_URL = "http://localhost:8000"


def generate_code(length: int = 6) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choices(alphabet, k=length))


@router.post("/links", response_model=LinkResponse, status_code=201)
async def create_link(payload: LinkCreate, db: AsyncSession = Depends(get_db)):
    code = payload.custom_code

    if code:
        existing = await db.scalar(select(Link).where(Link.code == code))
        if existing:
            raise HTTPException(status_code=409, detail="Code already in use")
    else:
        while True:
            code = generate_code()
            existing = await db.scalar(select(Link).where(Link.code == code))
            if not existing:
                break

    link = Link(
        code=code,
        original_url=str(payload.original_url),
        expires_at=payload.expires_at,
    )
    db.add(link)
    await db.commit()

    return LinkResponse(code=code, short_url=f"{BASE_URL}/{code}")


@router.get("/links/{code}", response_model=LinkMetadata)
async def get_link_metadata(code: str, db: AsyncSession = Depends(get_db)):
    link = await db.scalar(select(Link).where(Link.code == code))

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    return link


@router.delete("/links/{code}", status_code=204)
async def delete_link(code: str, db: AsyncSession = Depends(get_db)):
    link = await db.scalar(select(Link).where(Link.code == code))

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    await db.delete(link)
    await db.commit()
    await redis_client.delete(f"link:{code}")


@router.get("/{code}")
async def redirect_link(code: str, db: AsyncSession = Depends(get_db)):
    cached = await redis_client.get(f"link:{code}")
    if cached:
        return RedirectResponse(url=cached, status_code=302)

    link = await db.scalar(select(Link).where(Link.code == code))

    if not link:
        raise HTTPException(status_code=404, detail="Link not found")

    ttl = CACHE_TTL_SECONDS
    if link.expires_at:
        remaining = int((link.expires_at - datetime.now(timezone.utc)).total_seconds())
        if remaining <= 0:
            raise HTTPException(status_code=410, detail="Link expired")
        ttl = min(ttl, remaining)

    await redis_client.set(f"link:{code}", link.original_url, ex=ttl)
    return RedirectResponse(url=link.original_url, status_code=302)
