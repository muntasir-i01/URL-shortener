from fastapi import FastAPI

app = FastAPI()

from app.api.links import router as links_router

app.include_router(links_router)

@app.get("/health")
async def health():
    return {"status": "ok"}
