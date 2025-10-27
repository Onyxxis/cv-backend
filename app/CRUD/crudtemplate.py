from app.database import template_collection
from app.models.template import Template
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime

def template_helper(template) -> dict:
    return {
        "id": str(template["_id"]),
        "name": template["name"],
        "file_link": template["file_link"],
        "preview_image": template.get("preview_image"),
        "is_premium": template["is_premium"],
        "user_id": template["user_id"],
        "created_at": template["created_at"],
        "updated_at": template["updated_at"]
    }


# Creer un template
async def Create_template(template_data:dict)-> dict:
    template =await template_collection.insert_one(template_data)
    new_template = await template_collection.find_one({"_id":template.inserted_id})
    return template_helper(new_template)


# Lister tous les templates
async def Get_all_templates()-> list:
    templates =[]
    async for template in template_collection.find():
        templates.append(template_helper(template))
    return templates


# Avoir un template par son id
async def Get_template_by_id(template_id:str)-> dict:
    try:
        obj_id =ObjectId(template_id)
    except Exception:
        raise HTTPException(status_code=400,detail="Invalid templadte Id")
    template = await template_collection.find_one({"_id":obj_id})
    if not template:
        raise HTTPException(status_code=404, detail="Template not found ")
    return template_helper(template)


# Mettre a jour un template
async def Update_template(template_id:str, data:dict):
    try:
        obj_id = ObjectId(template_id)
    except Exception:
        raise HTTPException(status_code=400,detail="template id invalide")
    if not data:
        raise HTTPException(status_code=400,detail="Aucun mis a jour effectue")
    data["update_at"]= datetime.utcnow()
    result =await template_collection.update_one({"_id":obj_id},{"$set":data})
    if result.matched_count ==0:
        raise HTTPException(status_code=404,detail="Template non trouver")
    updated_template = await template_collection.find_one({"_id":obj_id})
    return template_helper(updated_template)


# supprimer un template
async def Delete_template(template_id:str):
    try:
        obj_id = ObjectId(template_id)
    except Exception:
        raise HTTPException(status_code=400,detail="template id invalide")
    result = await template_collection.delete_one({"_id":obj_id})
    if result.deleted_count ==0:
        raise HTTPException(status_code=404,detail="Template non trouver")
    return {"message":"Template supprimer avec succes"}


# Liste des template par utilisateur
async def Get_template_by_user(user_id:str):
    templates =[]
    async for template in template_collection.find({"user_id":user_id}):
        templates.append(template_helper(template)) 
    return templates 


# Liste par ispremium
async def Get_template_by_ispremium(is_premium:bool):
    templates =[]
    async for template in template_collection.find({"is_premium":is_premium}):
        templates.append(template_helper(template))
    return templates
