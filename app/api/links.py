import random
import string

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.link import Link
from app.schemas.link import LinkCreate, LinkResponse

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
