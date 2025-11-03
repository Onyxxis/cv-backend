from app.database import cv_collection  
from app.models.cv import CV
from bson import ObjectId
from fastapi import HTTPException,UploadFile
from datetime import datetime ,date
import io
import re
# from pdfplumber import PDF


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
        "updated_at": cv["updated_at"]
    }


# Create CV
async def create_cv(cv_data: dict) -> dict:
    cv_data["created_at"] = datetime.utcnow()
    cv_data["updated_at"] = datetime.utcnow()
    result = await cv_collection.insert_one(cv_data)
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
    try:
        obj_id = ObjectId(cv_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid CV ID")
    if not data:
        raise HTTPException(status_code=400, detail="No fields to update")
    data["updated_at"] = datetime.utcnow()
    result = await cv_collection.update_one({"_id": obj_id}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="CV not found")
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




# async def extract_cv_from_pdf(file: UploadFile, user_id: str) -> dict:
#     # Vérifier extension
#     if not file.filename.lower().endswith(".pdf"):
#         raise HTTPException(status_code=400, detail="Seuls les fichiers PDF sont acceptés")
    
#     # Lire le PDF
#     pdf_bytes = await file.read()
#     pdf_stream = io.BytesIO(pdf_bytes)

    # Extraire texte brut avec pdfplumber
#     try:
#         with PDF(pdf_stream) as pdf:
#             text = "\n".join(page.extract_text() or "" for page in pdf.pages)
#     except Exception:
#         raise HTTPException(
#             status_code=400,
#             detail="Impossible de lire le PDF. Assurez-vous que c'est un PDF texte (non scanné)"
#         )

#     if len(text.strip()) == 0:
#         raise HTTPException(status_code=400, detail="PDF vide ou scanné. Fournir un PDF texte lisible")

#     # --------------------------
#     # Informations personnelles
#     # --------------------------
#     # Email
#     email_match = re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
#     email = email_match.group(0) if email_match else ""

#     # Téléphone
#     phone_match = re.search(r"(\+?\d{1,4}[\s-]?)?(\d{2,3}[\s-]?){3,5}", text)
#     phone = phone_match.group(0) if phone_match else ""

#     # Nom / prénom via regex simple (première occurrence probable)
#     name_match = re.search(r"([A-Z][a-z]+(?: [A-Z][a-z]+)+)", text)
#     if name_match:
#         names = name_match.group(1).split()
#         first_name = names[0]
#         last_name = " ".join(names[1:])
#     else:
#         first_name, last_name = "", ""

#     # Titre / poste principal
#     title_match = re.search(
#         r"(Developer|Engineer|Analyst|Manager|Consultant|Designer|Data Scientist|Fullstack|Backend|Frontend)",
#         text, re.IGNORECASE
#     )
#     job_title = title_match.group(0) if title_match else ""

#     # --------------------------
#     # Expériences
#     # --------------------------
#     experiences = []
#     exp_pattern = re.compile(
#         r"(?:Experience|Professional Experience|Work Experience)\s*[:\n](.*?)(?:Education|Formation|Skills|Projects|$)",
#         re.DOTALL | re.IGNORECASE
#     )
#     exp_section = exp_pattern.search(text)
#     if exp_section:
#         lines = [l.strip() for l in exp_section.group(1).split("\n") if l.strip()]
#         for line in lines[:9]:
#             # Tenter d'extraire des années
#             dates = re.findall(r"(\d{4})", line)
#             start_date = date(int(dates[0]), 1, 1) if len(dates) > 0 else date.today()
#             end_date = date(int(dates[1]), 1, 1) if len(dates) > 1 else None
#             experiences.append({
#                 "position": line,
#                 "company": "",
#                 "description": "",
#                 "start_date": start_date,
#                 "end_date": end_date
#             })

#     # --------------------------
#     # Éducation
#     # --------------------------
#     education_list = []
#     edu_pattern = re.compile(
#         r"(?:Education|Formation)\s*[:\n](.*?)(?:Experience|Skills|Projects|$)",
#         re.DOTALL | re.IGNORECASE
#     )
#     edu_section = edu_pattern.search(text)
#     if edu_section:
#         lines = [l.strip() for l in edu_section.group(1).split("\n") if l.strip()]
#         for line in lines[:3]:
#             dates = re.findall(r"(\d{4})", line)
#             start_date = date(int(dates[0]), 1, 1) if len(dates) > 0 else date.today()
#             end_date = date(int(dates[1]), 1, 1) if len(dates) > 1 else None
#             education_list.append({
#                 "degree_name": line,
#                 "institution": "",
#                 "start_date": start_date,
#                 "end_date": end_date
#             })

#     # --------------------------
#     # Skills
#     # --------------------------
#     skills = []
#     skill_pattern = re.compile(r"(?:Skills|Compétences)\s*[:\n](.*?)(?:Experience|Education|Projects|$)", re.DOTALL | re.IGNORECASE)
#     skill_section = skill_pattern.search(text)
#     if skill_section:
#         skills_lines = re.split(r",|\n|-", skill_section.group(1))
#         skills = [{"name": s.strip()} for s in skills_lines if s.strip()]

#     # --------------------------
#     # Langues
#     # --------------------------
#     languages = []
#     lang_pattern = re.compile(r"(?:Languages|Langues)\s*[:\n](.*?)(?:Experience|Education|Skills|$)", re.DOTALL | re.IGNORECASE)
#     lang_section = lang_pattern.search(text)
#     if lang_section:
#         langs = re.split(r",|\n", lang_section.group(1))
#         languages = [{"name": l.strip(), "level": "intermediate"} for l in langs if l.strip()]

#     # --------------------------
#     # Construction CV
#     # --------------------------
#     cv_data = {
#         "user_id": user_id,
#         "template_id": None,
#         "title": job_title,
#         "personal_info": {
#             "first_name": first_name,
#             "last_name": last_name,
#             "birthdate": date(2000,1,1),
#             "gender": "",
#             "email": email,
#             "phone": phone,
#             "nationality": None,
#             "job_title": job_title,
#             "description": "",
#             "link": ""
#         },
#         "experiences": experiences,
#         "education": education_list,
#         "skills": skills,
#         "projects": [],
#         "languages": languages,
#         "certifications": [],
#         "created_at": datetime.utcnow(),
#         "updated_at": datetime.utcnow()
#     }

#     # Validation stricte via Pydantic
#     cv_obj = CV(**cv_data)
#     return cv_obj.dict()
