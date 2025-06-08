from fastapi import APIRouter, HTTPException
import feedparser
import httpx
from typing import Optional

router = APIRouter()

@router.get("/latest-movie")
async def get_latest_movie():
    """Récupère le dernier film vu sur Letterboxd"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://letterboxd.com/hugyouu/rss/")
            feed = feedparser.parse(response.text)
            
        if not feed.entries:
            raise HTTPException(status_code=404, detail="Aucun film trouvé")
            
        latest = feed.entries[0]
        return {
            "title": latest.title,
            "link": latest.link,
            "published": latest.published,
            "summary": latest.summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")