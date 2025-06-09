from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import letterboxd, watchlist

app = FastAPI(
    title="Mon API Personnelle",
    description="API REST pour diverses ressources",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(letterboxd.router, prefix="/letterboxd", tags=["letterboxd"])
app.include_router(watchlist.router, prefix="/watchlist", tags=["watchlist"])

@app.get("/")
async def root():
    return {
        "message": "API opérationnelle", 
        "status": "running",
        "docs": "https://api.hugo-pierret.be/docs",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
