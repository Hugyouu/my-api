from fastapi import APIRouter, HTTPException, UploadFile, File
from pathlib import Path
import pandas as pd
import random
from typing import Optional
import os

router = APIRouter()

WATCHLIST_PATH = Path("app/data/watchlist.csv")

def load_watchlist():
    """Charge la watchlist depuis le CSV"""
    if not WATCHLIST_PATH.exists():
        raise HTTPException(status_code=404, detail="Watchlist non trouvée. Uploadez d'abord votre CSV.")
    
    try:
        df = pd.read_csv(WATCHLIST_PATH)
        # Les colonnes typiques d'une watchlist Letterboxd
        required_columns = ['Name', 'Year']
        if not all(col in df.columns for col in required_columns):
            raise HTTPException(status_code=400, detail="Format CSV invalide")
        return df
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lecture CSV: {str(e)}")

@router.get("/random")
async def get_random_movie():
    """Retourne un film aléatoire de la watchlist"""
    df = load_watchlist()
    
    if df.empty:
        raise HTTPException(status_code=404, detail="Watchlist vide")
    
    # Sélection aléatoire
    random_movie = df.sample(n=1).iloc[0]
    
    # Construction de la réponse avec gestion des valeurs manquantes
    movie_data = {
        "title": random_movie.get('Name', 'Titre inconnu'),
        "year": random_movie.get('Year', None),
        "letterboxd_uri": random_movie.get('Letterboxd URI', None),
        "total_movies_in_watchlist": len(df)
    }
    
    # Nettoyage des valeurs NaN
    movie_data = {k: (v if pd.notna(v) else None) for k, v in movie_data.items()}
    
    return movie_data

@router.post("/upload")
async def upload_watchlist(file: UploadFile = File(...)):
    """Upload un nouveau fichier watchlist CSV"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Seuls les fichiers CSV sont acceptés")
    
    try:
        # Créer le dossier data s'il n'existe pas
        WATCHLIST_PATH.parent.mkdir(exist_ok=True)
        
        # Sauvegarder le fichier
        content = await file.read()
        with open(WATCHLIST_PATH, 'wb') as f:
            f.write(content)
        
        # Vérifier que le CSV est valide
        df = pd.read_csv(WATCHLIST_PATH)
        
        return {
            "message": "Watchlist mise à jour avec succès",
            "movies_count": len(df),
            "columns": list(df.columns)
        }
    
    except Exception as e:
        # Supprimer le fichier en cas d'erreur
        if WATCHLIST_PATH.exists():
            os.remove(WATCHLIST_PATH)
        raise HTTPException(status_code=500, detail=f"Erreur upload: {str(e)}")

@router.delete("/")
async def clear_watchlist():
    """Supprime la watchlist"""
    if WATCHLIST_PATH.exists():
        os.remove(WATCHLIST_PATH)
        return {"message": "Watchlist supprimée"}
    else:
        raise HTTPException(status_code=404, detail="Aucune watchlist à supprimer")