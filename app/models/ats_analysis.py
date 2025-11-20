import datetime
from pydantic import BaseModel, Field
from typing import List, Optional

class ATSAnalysis(BaseModel):
    cv_id: str = Field(..., description="ID du CV analysé")
    score: int = Field(..., description="Score ATS sur 100")
    summary: str = Field(..., description="Résumé professionnel")
    improvements: List[str] = Field(default_factory=list, description="Suggestions d'amélioration")
    keyword_recommendations: List[str] = Field(default_factory=list, description="Mots-clés recommandés")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Date de création de l'analyse")
