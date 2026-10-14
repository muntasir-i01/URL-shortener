from fastapi import FastAPI

from app.api.links import router as links_router

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(links_router)
