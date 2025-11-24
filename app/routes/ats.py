import asyncio
from fastapi import APIRouter, HTTPException
from app.models.cv import CV
from app.CRUD.gemini_analyzer import analyze_cv_with_gemini
from app.config import settings
import google.generativeai as genai


genai.configure(api_key=settings.gemini_api_key)


router = APIRouter(
    prefix="/ats",
    tags=["ATS Analysis"]
    )


@router.post("/analyze")
async def analyze_cv(cv_data: dict):
    try:
        result = await analyze_cv_with_gemini(cv_data)
        return {"status": "success", "analysis": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))