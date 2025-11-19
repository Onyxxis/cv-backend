import json
from app.database import cv_collection  
from app.models.cv import CV, ExtractedCVData
from bson import ObjectId
from fastapi import HTTPException,UploadFile
from datetime import datetime ,date
import io
import re
from typing import List, Optional
from fastapi.encoders import jsonable_encoder
import mimetypes
from app.config import settings
import google.generativeai as genai
from datetime import datetime, date


MODEL_NAME = "models/gemini-2.5-pro"

genai.configure(api_key=settings.gemini_api_key)


def cv_helper(cv) -> dict:
    return {
        "id": str(cv["_id"]),
        "user_id": cv["user_id"],
        "template_id": cv.get("template_id"),
        "title": cv["title"],
        "personal_info": cv["personal_info"],
        "experiences": cv.get("experiences", []),
        "education": cv.get("education", []),
        "skills": cv.get("skills", []),
        "projects": cv.get("projects", []),
        "languages": cv.get("languages", []),
        "certifications": cv.get("certifications", []),
        "created_at": cv["created_at"],
        "updated_at": cv["updated_at"],
        "completion_percentage": cv.get("completion_percentage", 0),    
        "is_completed": cv.get("is_completed", False),  
    }

def calculate_completion(cv_data):
    sections = {
        "personal_info": 20,
        "experiences": 20 if len(cv_data.get("experiences", [])) > 0 else 0,
        "education": 15 if len(cv_data.get("education", [])) > 0 else 0,
        "skills": 15 if len(cv_data.get("skills", [])) > 0 else 0,
        "projects": 10 if len(cv_data.get("projects", [])) > 0 else 0,
        "languages": 10 if len(cv_data.get("languages", [])) > 0 else 0,
        "certifications": 10 if len(cv_data.get("certifications", [])) > 0 else 0,
    }

    total = 0

    if cv_data.get("personal_info"):
        if cv_data["personal_info"].get("first_name") and cv_data["personal_info"].get("last_name"):
            total += sections["personal_info"]

    total += sections["experiences"]
    total += sections["education"]
    total += sections["skills"]
    total += sections["projects"]
    total += sections["languages"]
    total += sections["certifications"]

    return min(total, 100)



#     return cv_helper(new_cv)
async def create_cv(cv_data: dict) -> dict:
    # Ajout des dates de création / modification
    cv_data["created_at"] = datetime.utcnow()
    cv_data["updated_at"] = datetime.utcnow()

    # Calcul du pourcentage de complétion
    completion = calculate_completion(cv_data)
    cv_data["completion_percentage"] = completion
    cv_data["is_completed"] = (completion == 100)

    # ✅ Transformation en format encodable JSON (dates → ISO string)
    cv_data_encodable = jsonable_encoder(cv_data)

    # Insertion dans MongoDB
    result = await cv_collection.insert_one(cv_data_encodable)
    new_cv = await cv_collection.find_one({"_id": result.inserted_id})

    return cv_helper(new_cv)



# Get all CVs
async def get_all_cvs() -> list:
    cvs = []
    async for cv in cv_collection.find():
        cvs.append(cv_helper(cv))
    return cvs


# Get CV by ID
async def get_cv_by_id(cv_id: str) -> dict:
    try:
        obj_id = ObjectId(cv_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CV ID")
    cv = await cv_collection.find_one({"_id": obj_id})
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    return cv_helper(cv)


# Update CV
async def update_cv(cv_id: str, data: dict) -> dict:
    from datetime import datetime
    try:
        obj_id = ObjectId(cv_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CV ID")

    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")

    existing_cv = await cv_collection.find_one({"_id": obj_id})
    if not existing_cv:
        raise HTTPException(status_code=404, detail="CV not found")

    updated_cv_data = {**existing_cv, **data}
    updated_cv_data["updated_at"] = datetime.utcnow()

    completion = calculate_completion(updated_cv_data)
    updated_cv_data["completion_percentage"] = completion
    updated_cv_data["is_completed"] = (completion == 100)
    await cv_collection.update_one(
        {"_id": obj_id},
        {"$set": updated_cv_data}
    )
    updated_cv = await cv_collection.find_one({"_id": obj_id})
    return cv_helper(updated_cv)




# Delete CV
async def delete_cv(cv_id: str) -> dict:
    try:
        obj_id = ObjectId(cv_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CV ID")
    result = await cv_collection.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="CV not found")
    return {"message": "CV deleted successfully"}



# Get CVs by User
async def get_cvs_by_user(user_id: str) -> list:
    cvs = []
    async for cv in cv_collection.find({"user_id": user_id}):
        cvs.append(cv_helper(cv))
    return cvs


# Get the last created CV of a user
async def get_last_cv_by_user(user_id: str) -> dict:
    cv = await cv_collection.find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)]
    )
    if not cv:
        return {"title": "Aucun CV", "completion_percentage": 0, "created_at": None}
    return cv_helper(cv)



async def get_completed_cvs_by_user(user_id: str) -> list:
    cvs = []
    async for cv in cv_collection.find({"user_id": user_id, "is_completed": True}):
        cvs.append(cv_helper(cv))
    return cvs


 
async def get_in_progress_cvs_by_user(user_id: str) -> list:
    cvs = []
    async for cv in cv_collection.find({"user_id": user_id, "is_completed": False}):
        cvs.append(cv_helper(cv))
    return cvs


# pour avoir le nombre total  de cv complet et non complet 
async def get_cv_process_by_user(user_id: str) -> dict:
    total_complete = await cv_collection.count_documents({"user_id": user_id, "is_completed": True})
    total_in_progress = await cv_collection.count_documents({"user_id": user_id, "is_completed": False})

    return {
        "completed_cvs": total_complete,
        "in_progress_cvs": total_in_progress
    }



async def get_recent_cvs_crud(limit: int = 4) -> List[CV]:
    """
    Retourne les derniers CVs créés, triés par date de création décroissante.
    """
    cvs = await get_all_cvs()
    if not cvs:
        return []

    # Trier par date de création
    sorted_cvs = sorted(cvs, key=lambda x: x.get("created_at", datetime.min), reverse=True)
    recent_cvs = sorted_cvs[:limit]

    # Formater pour retourner un objet CV complet
    formatted_cvs = []
    for cv in recent_cvs:
        try:
            formatted_cvs.append(CV(**cv))
        except Exception as e:
            print(f"CV invalide ignoré: {cv.get('id', 'unknown')} - {e}")

    return formatted_cvs


def extract_json(text: str):
    """
    Extrait un JSON valide depuis n'importe quel texte généré par Gemini.
    """
    import re
    text = re.sub(r"```json|```", "", text).strip()
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(text.replace("'", '"'))
    except:
        return None



def normalize_cv_data(raw: dict) -> dict:
    """Convertit le JSON brut de Gemini en format compatible avec ExtractedCVData"""

    # --- Personal Info ---
    pi = raw.get("personal_info", {})
    pi["birthdate"] = parse_date(pi.get("birthdate")) or None
    raw["personal_info"] = pi

    # --- Experiences ---
    exps = []
    for exp in raw.get("experiences", []):
        exps.append({
            "position": exp.get("position") or "",
            "company": exp.get("company") or "",
            "description": exp.get("description") or "",
            "start_date": parse_date(exp.get("start_date")) or None,
            "end_date": parse_date(exp.get("end_date")) or None,
        })
    raw["experiences"] = exps

    # --- Education ---
    edus = []
    for edu in raw.get("education", []):
        edus.append({
            "degree_name": edu.get("degree_name") or edu.get("degree") or "",
            "institution": edu.get("institution") or "",
            "start_date": parse_date(edu.get("start_date")) or None,
            "end_date": parse_date(edu.get("end_date")) or None,
        })
    raw["education"] = edus

    # --- Skills ---
    skills_normalized = []
    for s in raw.get("skills", []):
        if isinstance(s, str):
            skills_normalized.append({"name": s})
        elif isinstance(s, dict):
            # Si Gemini renvoie {'category': 'Front-end', 'items': ['React', 'Vue']}
            items = s.get("items", [])
            for item in items:
                skills_normalized.append({"name": item})
            # Si déjà un champ name
            if "name" in s:
                skills_normalized.append({"name": s["name"]})
    raw["skills"] = skills_normalized

    # --- Projects ---
    projs = []
    for p in raw.get("projects", []):
        projs.append({
            "name": p.get("name") or "",
            "description": p.get("description") or "",
            "start_date": parse_date(p.get("start_date")) or None,
            "end_date": parse_date(p.get("end_date")) or None,
        })
    raw["projects"] = projs

    # --- Languages ---
    langs = []
    for l in raw.get("languages", []):
        langs.append({
            "name": l.get("name") or l.get("language") or "",
            "level": l.get("level") or "",
        })
    raw["languages"] = langs

    # --- Certifications ---
    certs = []
    for c in raw.get("certifications", []):
        certs.append({
            "title": c.get("title") or "",
            "organization": c.get("organization") or "",
            "date_obtained": parse_date(c.get("date_obtained")) or None,
            "url": c.get("url") or None,
        })
    raw["certifications"] = certs

    return raw



def parse_date(value):
    """Convertit une chaîne en date ou retourne None si impossible"""
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        # Essaie YYYY-MM-DD
        return datetime.strptime(value, "%Y-%m-%d").date()
    except:
        try:
            # Essaie YYYY-MM
            return datetime.strptime(value, "%Y-%m").date()
        except:
            try:
                # Essaie juste YYYY
                return datetime.strptime(value, "%Y").date()
            except:
                return None


async def process_cv_import(file: UploadFile) -> ExtractedCVData:
    try:
        # Lire le contenu du fichier
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Fichier vide")

        # Détecter le mime type
        mime = file.content_type or mimetypes.guess_type(file.filename)[0] or "application/octet-stream"

        # Construire le prompt pour Gemini
        prompt = f"""
Lis ce CV fourni (mime_type={mime}) et extrait toutes les informations dans ce format strict JSON :
{{
    "personal_info": {{
        "first_name": "",
        "last_name": "",
        "birthdate": null,
        "gender": "",
        "email": "",
        "phone": "",
        "nationality": "",
        "job_title": "",
        "description": "",
        "link": ""
    }},
    "experiences": [],
    "education": [],
    "skills": [],
    "projects": [],
    "languages": [],
    "certifications": []
}}

Si une info n’est pas trouvée, laisse une chaîne vide ou null.
Respecte strictement les noms des clés.
Voici le contenu du CV encodé en UTF-8 : {content.decode('utf-8', errors='ignore')}
"""

        # Appel à Gemini
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)

        # Récupérer le texte généré
        text_output = getattr(response, "output_text", None) or getattr(response, "text", "")

        # Extraire le JSON strict
        data = extract_json(text_output)
        if not data:
            raise HTTPException(status_code=500, detail=f"Impossible d'extraire le JSON du CV. Output brut : {text_output}")

        # ✅ Normaliser les données pour Pydantic (dates, skills, languages, etc.)
        normalized_data = normalize_cv_data(data)
        # Retourner un objet Pydantic validé
        return ExtractedCVData(**normalized_data)

    except Exception as e:
        print("IMPORT ERROR:", e)
        raise HTTPException(status_code=500, detail="Erreur lors de l'import du CV")
