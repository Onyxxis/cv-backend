
import json
import re
from datetime import datetime
from app.config import settings
import google.generativeai as genai
from app.CRUD.ats_analysis_crud import save_ats_analysis  
from app.models.cv import ExtractedCVData, CV

genai.configure(api_key=settings.gemini_api_key)
MODEL_NAME = "models/gemini-2.5-pro"


def extract_json(text: str):
    """
    Extrait un JSON valide depuis n'importe quel texte (Markdown, texte avant/après, etc.).
    """
    # 1. Enlever les blocs ```json ... ```
    text = re.sub(r"```json|```", "", text).strip()

    # 2. Tenter d'extraire le premier objet JSON { ... }
    json_match = re.search(r"\{[\s\S]*\}", text)
    if json_match:
        json_str = json_match.group(0)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    # 3. Tentative brute : remplacer quotes simples
    try:
        return json.loads(text.replace("'", '"'))
    except:
        return None


# async def analyze_cv_with_gemini(cv_data: dict):
#     """
#     Analyse un CV via Gemini et retourne le JSON d'analyse ATS.
#     Enregistre automatiquement l'analyse dans MongoDB.
#     """
#     cv_id = cv_data.get("id")
#     if not cv_id:
#         return {"error": "Le CV doit contenir un ID pour l'enregistrement."}

#     # Analyse via Gemini
#     prompt = f"""
#     Tu es une intelligence spécialisée en analyse ATS professionnelle.

#     Analyse le CV suivant (fourni au format JSON) et produis STRICTEMENT ce JSON :

#     {{
#         "score": <int>,
#         "summary": "<résumé professionnel>",
#         "improvements": ["<suggestion 1>", "<suggestion 2>"],
#         "keyword_recommendations": ["<keyword 1>", "<keyword 2>"]
#     }}

#     N'ajoute pas de texte avant ou après. Seulement le JSON.
#     Voici le CV à analyser :
#     {cv_data}
#     """

#     model = genai.GenerativeModel(MODEL_NAME)
#     response = model.generate_content(prompt)

#     text = getattr(response, "output_text", None) or getattr(response, "text", "")
#     extracted = extract_json(text)

#     if not extracted:
#         return {
#             "error": "Format JSON invalide",
#             "raw": text
#         }

#     try:
#         # ajouter created_at avant l'enregistrement
#         extracted["created_at"] = datetime.utcnow()
#         await save_ats_analysis(cv_id, extracted)
#     except Exception as e:
#         extracted["save_error"] = str(e)

#     return extracted

async def analyze_cv_with_gemini(cv_data: dict):
    """
    Analyse un CV via Gemini et retourne le JSON d'analyse ATS.
    Ne l'enregistre pas en base de données.
    """

    # Convertir le dict reçu en objet Pydantic pour validation
    extracted_cv = ExtractedCVData(**cv_data)

    # Transformer en JSON normalisé pour l'analyse
    # cv_data_normalized = extracted_cv.json(indent=2)
    cv_data_normalized = extracted_cv.model_dump_json(indent=2)

    # cv_data_normalized = json.dumps(extracted_cv.model_dump(), indent=2, ensure_ascii=False)


    prompt = f"""
Tu es une intelligence spécialisée en analyse ATS professionnelle.

Analyse le CV suivant (fourni au format JSON) et produis STRICTEMENT ce JSON :

{{
    "score": <int>,
    "summary": "<résumé professionnel>",
    "improvements": ["<suggestion 1>", "<suggestion 2>"],
    "keyword_recommendations": ["<keyword 1>", "<keyword 2>"]
}}

N'ajoute pas de texte avant ou après. Seulement le JSON.
Voici le CV à analyser :
{cv_data_normalized}
"""

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)

    text = getattr(response, "output_text", None) or getattr(response, "text", "")
    extracted = extract_json(text)

    if not extracted:
        extracted = {
            "score": 0,
            "summary": "",
            "improvements": [],
            "keyword_recommendations": [],
            "raw": text
        }
    else:
        extracted["created_at"] = datetime.utcnow()

    return extracted



async def reformulate_text(text: str, context: str = "") -> str:
    """
    Envoie le texte à Gemini pour générer une reformulation adaptée à un CV.
    Le 'context' peut préciser la section (ex: 'information personnelle', 'projet').
    """
    prompt = f"""
    Tu es un expert en rédaction professionnelle de CV.
    
    Reformule le texte ci-dessous pour le rendre plus clair, fluide,
    professionnel et agréable à lire, tout en restant concis et adapté à un CV.

    Règles strictes :
    - Ne rien inventer, ne rien ajouter.
    - Garder le même sens, les mêmes faits et l’intention d’origine.
    - Améliorer la formulation pour la rendre élégante, naturelle et engageante.
    - Style recherché : professionnel, moderne, dynamique, percutant.
    - Phrases longues et élégantes autorisées, mais sans lourdeur, sans complexité inutile et sans commentaires superflus.

    
    Section / Contexte : {context}

    Texte à reformuler : "{text}"

    Répond uniquement avec la version reformulée.
    """

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)
    output_text = getattr(response, "output_text", None) or getattr(response, "text", "")
    return output_text.strip()
