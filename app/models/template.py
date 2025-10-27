from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class Template(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    file_link: str= Field(..., min_length=1, max_length=400)
    preview_image: Optional[str] =Field (None,description="Lien vers l'image de prévisualisation du template", max_length=400)
    is_premium: bool =Field(False, description="Indique si le template est premium ou non")
    user_id: str = Field(..., description="ID de l'utilisateur qui a créé le template")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class config:
        scheama_extra = {
            "example": {
                "name": "Template 1",
                "file_link": "http://example.com/template1",
                "preview_image": "http://example.com/preview1.png",
                "is_premium": False,
                "user_id": "60d0fe4f5311236168a109ca"
            }
        }