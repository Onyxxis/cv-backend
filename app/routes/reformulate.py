# app/routers/reformulate.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.CRUD.gemini_analyzer import reformulate_text

router = APIRouter(
    prefix="/reformulate",
    tags=["Reformulation"]
)

class ReformulateRequest(BaseModel):
    text: str
    context: str = ""  

class ReformulateResponse(BaseModel):
    reformulated_text: str


@router.post("/", response_model=ReformulateResponse)
async def reformulate_endpoint(request: ReformulateRequest):
    try:
        reformulated = await reformulate_text(request.text, request.context)
        return {"reformulated_text": reformulated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
