from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.settings import get_settings

settings = get_settings()
app = FastAPI(title="Ness GPT API", version="0.1.0")


def _build_allowed_origins() -> list[str]:
    configured = [origin.strip() for origin in settings.frontend_origin.split(",") if origin.strip()]
    defaults = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ]

    seen: set[str] = set()
    allowed: list[str] = []
    for origin in configured + defaults:
        if origin not in seen:
            seen.add(origin)
            allowed.append(origin)

    return allowed

app.add_middleware(
    CORSMiddleware,
    allow_origins=_build_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(api_router)
