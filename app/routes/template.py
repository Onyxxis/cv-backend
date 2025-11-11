from fastapi import APIRouter, HTTPException, Query
from app.CRUD.crudtemplate import (Create_template, Get_all_templates, Get_template_by_id, Update_template, Delete_template, Get_template_by_user,Get_template_by_ispremium)
from app.models.template import Template
from fastapi.responses import HTMLResponse


router = APIRouter(
    prefix="/templates",
    tags=["Templates"]
)

# creer un template
@router.post("", summary="Créer un template")
async def create(template: Template):
    template_dict = template.dict()
    new_template = await Create_template(template_dict)
    return {"message": "Template créé avec succès", "template": new_template}


# lister tous les templates
@router.get("", summary="Obtenir tous les templates")
async def get_templates():
    templates = await Get_all_templates()
    return {"total": len(templates), "templates": templates}


# FILTER BY PREMIUM STATUS
@router.get("/filter/premium", summary="Lister les templates par statut premium")
async def get_templates_by_premium(is_premium: bool = Query(..., description="Statut premium (true ou false)")):
    templates = await Get_template_by_ispremium(is_premium)
    return {"total": len(templates), "templates": templates}


# FILTER BY USER
@router.get("/filter/user", summary="Lister les templates par utilisateur")
async def get_templates_by_user(user_id: str = Query(..., description="ID de l'utilisateur")):
    templates = await Get_template_by_user(user_id)
    return {"total": len(templates), "templates": templates}


# GET BY ID
@router.get("/{template_id}", summary="Obtenir un template par ID")
async def get_template_by_id(template_id: str):
    template = await Get_template_by_id(template_id)
    return {"template": template}


# UPDATE
@router.put("/{template_id}", summary="Mettre à jour un template par ID")
async def update_template(template_id: str, data: dict):
    updated_template = await Update_template(template_id, data)
    return {"message": "Template mis à jour avec succès", "template": updated_template}


# DELETE
@router.delete("/{template_id}", summary="Supprimer un template par ID")
async def delete_template(template_id: str):
    result = await Delete_template(template_id)
    return result














@router.get("/{template_id}/file", response_class=HTMLResponse)
async def get_template_file(template_id: str):
    template = await get_template_by_id(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template non trouvé")
    
    try:
        with open(template["file_link"], "r", encoding="utf-8") as f:
            html_content = f.read()
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Fichier HTML introuvable")
    
    return HTMLResponse(content=html_content)




