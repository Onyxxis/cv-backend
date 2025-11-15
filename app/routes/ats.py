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
async def analyze_cv(cv: CV):
    try:
        cv_dict = cv.dict()
        cv_dict.pop("title", None)
        cv_dict.pop("template_id", None)

        result = await asyncio.to_thread(analyze_cv_with_gemini, cv_dict)
        return {"status": "success", "analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test-gemini")
async def test_gemini():
    try:
        model = genai.GenerativeModel("models/gemini-2.5-pro")

        response = model.generate_content("Dis-moi simplement : 'Gemini fonctionne 👌 bizzzouu ar'")

        # Récupération sûre du texte généré
        text = getattr(response, "output_text", None) or getattr(response, "text", "")

        return {
            "status": "success",
            "response": text
        }

    except Exception as e:
        return {
            "status": "error",
            "detail": str(e)
        }


@router.get("/list-gemini-models")
async def list_gemini_models():
    try:

        genai.configure(api_key=settings.gemini_api_key)

        models = genai.list_models()
        return {
            "status": "success",
            "available_models": models
        }
    except Exception as e:
        return {
            "status": "error",
            "detail": str(e)
        }
