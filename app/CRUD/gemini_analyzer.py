import json
import os

from app.config import settings
import google.generativeai as genai
from datetime import datetime

# Charger API Key
# API_KEY = os.getenv("GEMINI_API_KEY")

# genai.configure(api_key=API_KEY)

genai.configure(api_key=settings.gemini_api_key)

MODEL_NAME = "models/gemini-2.5-pro"


def analyze_cv_with_gemini(cv_data: dict):
    """
    Analyse ATS complète : score + suggestions.
    Retourne un dictionnaire avec les clés :
        - score
        - summary
        - improvements
        - keyword_recommendations
    """
    
    prompt = f"""
    Tu es une intelligence spécialisée en analyse ATS professionnelle.

    Analyse le CV suivant (fourni au format JSON) et produis :
    1. Un score ATS sur 100
    2. Une évaluation détaillée de :
        - la structure
        - la clarté
        - l'impact du contenu
        - la cohérence
        - les mots-clés manquants (ATS)
        - l'adéquation professionnelle (soft & hard skills)
    3. Donne des suggestions concrètes d'amélioration.
    4. Retourne tout sous forme d'un JSON strict, au format :

    {{
        "score": <int>,
        "summary": "<résumé professionnel>",
        "improvements": [
            "<suggestion 1>",
            "<suggestion 2>"
        ],
        "keyword_recommendations": [
            "<keyword 1>", "<keyword 2>"
        ]
    }}

    Voici le CV à analyser :
    {cv_data}
    """

    model = genai.GenerativeModel(MODEL_NAME)
    # Appel Gemini
    response = model.generate_content(prompt)
    
    # Récupération sûre du texte généré
    text = getattr(response, "output_text", None) or getattr(response, "text", "")

    # Parsing JSON tolérant
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        try:
            # Tentative simple de correction des quotes simples
            cleaned = text.replace("'", '"')
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Retourne le texte brut si tout échoue
            return {"error": "Format JSON invalide", "raw": text}