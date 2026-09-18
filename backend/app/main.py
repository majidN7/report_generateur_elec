from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import bureaux, bureaux_centraux, import_router

app = FastAPI(title="Gestion des Bureaux de Vote", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition", "X-Skipped-Incomplete"],
)

app.include_router(import_router.router)
app.include_router(bureaux.router)
app.include_router(bureaux_centraux.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
