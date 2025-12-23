import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.models.cv import CV
from app.CRUD.gemini_analyzer import analyze_cv_with_gemini
from app.config import settings
import google.generativeai as genai
from app.CRUD.ats_analysis_crud import (
    get_average_score,
    save_ats_analysis,
    get_analysis_by_cv,
    update_ats_analysis,
    get_all_analyses
)

genai.configure(api_key=settings.gemini_api_key)


router = APIRouter(
    prefix="/ats",
    tags=["ATS Analysis"]
    )


# @router.post("/analyze")
# async def analyze_cv(cv_data: dict):
#     try:
#         result = await analyze_cv_with_gemini(cv_data)
#         return {"status": "success", "analysis": result}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
# @router.post("/analyze")
# async def analyze_cv(cv_data: dict):
#     """
#     Endpoint pour analyser un CV complet.
#     cv_data doit correspondre au modèle ExtractedCVData.
#     """
#     try:
#         # Appeler Gemini pour analyse
#         result = await analyze_cv_with_gemini(cv_data)
#         return {"status": "success", "analysis": result}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/analyze")
async def analyze_cv_mock(cv_data: dict):
    # Mock de test pour Swagger sans consommer de quota
    mock_result = {
    "score": 90,  # CV bien structuré, complet et compatible ATS
    "summary": "CV bien rédigé pour un poste de Comptable, détaillant expériences professionnelles, compétences techniques et projets pertinents.",
    "improvements": [
        "Ajouter plus de détails chiffrés sur les réalisations dans les expériences professionnelles",
        "Optimiser les mots-clés liés aux logiciels comptables et aux normes IFRS"
    ],
    "keyword_recommendations": [
        "Comptabilité générale",
        "Analyse financière",
        "Gestion budgétaire",
        "Fiscalité",
        "Sage Comptabilité",
        "Excel avancé"
    ],
    "created_at": datetime.utcnow()
    }
    return {"status": "success", "analysis": mock_result}


@router.get("/average-score")
async def average_score():
    try:
        avg = await get_average_score()
        return {
            "status": "success",
            "average_score": round(avg, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

