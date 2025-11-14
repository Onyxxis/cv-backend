# app/routes/upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.CRUD.cloudinary import upload_to_cloudinary
import traceback
import asyncio
import mimetypes

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

@router.post("/")
async def upload_file(file: UploadFile = File(...), folder: str = Form("uploads")):
    try:
        file_bytes = await file.read()
        if len(file_bytes) == 0:
            raise HTTPException(status_code=400, detail="Fichier vide")

        # Détecter le type MIME (pour info seulement)
        mime_type, _ = mimetypes.guess_type(file.filename)
        is_raw = mime_type in ["text/html", "application/pdf", "text/plain"]

        # Upload en thread pour ne pas bloquer l'event loop
        # ⚠️ On ne passe plus resource_type, la fonction gère déjà raw par défaut
        upload_result = await asyncio.to_thread(
            upload_to_cloudinary,
            file_bytes,
            folder,
            file.filename  # filename
        )

        return {
            "filename": file.filename,
            "public_id": upload_result["public_id"],
            "secure_url": upload_result["secure_url"],
            "resource_type": upload_result["resource_type"],
            "raw_link": upload_result["raw_link"],  # lien direct partageable
        }

    except Exception as e:
        print("Erreur lors de l'upload :")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
