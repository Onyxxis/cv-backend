from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from app.CRUD.email_service import send_welcome_email

router = APIRouter(
    prefix="/email", 
    tags=["Email"])

class EmailRequest(BaseModel):
    email: EmailStr
    username: str

@router.post("/send-email")
async def send_welcome(req: EmailRequest):
    success = send_welcome_email(req.email, req.username)
    return {"status": "sent" if success else "failed"}
