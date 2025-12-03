from datetime import datetime
from bson import ObjectId
from app.database import ats_analysis_collection
from app.models.ats_analysis import ATSAnalysis
from typing import Optional

# Helper pour formater les analyses
def analysis_helper(analysis) -> dict:
    return {
        "id": str(analysis["_id"]),
        "cv_id": analysis["cv_id"],
        "score": analysis["score"],
        "summary": analysis["summary"],
        "improvements": analysis.get("improvements", []),
        "keyword_recommendations": analysis.get("keyword_recommendations", []),
        "created_at": analysis.get("created_at"),
    }

# Enregistrer une nouvelle analyse ATS
async def save_ats_analysis(cv_id: str, analysis: dict) -> dict:
    data = {
        "cv_id": cv_id,
        "score": analysis.get("score"),
        "summary": analysis.get("summary"),
        "improvements": analysis.get("improvements", []),
        "keyword_recommendations": analysis.get("keyword_recommendations", []),
        "created_at": datetime.utcnow()
    }

    result = await ats_analysis_collection.insert_one(data)
    new_analysis = await ats_analysis_collection.find_one({"_id": result.inserted_id})
    return analysis_helper(new_analysis)

# Vérifier si une analyse existe pour un CV donné
async def get_analysis_by_cv(cv_id: str) -> Optional[dict]:
    analysis = await ats_analysis_collection.find_one({"cv_id": cv_id})
    if analysis:
        return analysis_helper(analysis)
    return None

# Mettre à jour une analyse existante
async def update_ats_analysis(cv_id: str, analysis: dict) -> dict:
    update_data = {
        "score": analysis.get("score"),
        "summary": analysis.get("summary"),
        "improvements": analysis.get("improvements", []),
        "keyword_recommendations": analysis.get("keyword_recommendations", []),
        "created_at": datetime.utcnow()  # mise à jour de la date
    }
    await ats_analysis_collection.update_one({"cv_id": cv_id}, {"$set": update_data})
    updated = await ats_analysis_collection.find_one({"cv_id": cv_id})
    return analysis_helper(updated)


# Récupérer toutes les analyses ATS
async def get_all_analyses():
    analyses = []
    async for analysis in ats_analysis_collection.find():
        analyses.append(analysis_helper(analysis))
    return analyses

# Récupérer tous les scores uniquement
async def get_all_scores() -> list:
    scores = []
    async for analysis in ats_analysis_collection.find({}, {"score": 1}):
        if "score" in analysis and isinstance(analysis["score"], (int, float)):
            scores.append(analysis["score"])
    return scores


async def get_average_score() -> float:
    scores = await get_all_scores()
    if not scores:
        return 0  
    
    return sum(scores) / len(scores)
