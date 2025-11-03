from fastapi import APIRouter, HTTPException, Query
from app.CRUD.cruduser import (
    Create_utilisateur,
    Get_all_utilisateurs,
    Get_utilisateur_by_id,
    Update_utilisateur,
    Delete_utilisateur,
    Get_utilisateurs_by_role,
    Get_utilisateurs_by_ispremium,
    Change_utilisateur_ispremium_status
    ,Get_utilisateurs_by_ispremium_and_role

)
from app.models.User import Utilisateur,Role

router = APIRouter(
    prefix="/users",   
    tags=["Utilisateurs"]   
)


#creer un utilisateur
@router.post("", summary="Créer un utilisateur")
async def create_user(user: Utilisateur):
    user_dict = user.dict()  
    new_user = await Create_utilisateur(user_dict)
    return {"message": "Utilisateur créé avec succès","utilisateur":new_user}


# lister utilisateur
@router.get("",summary="Obtenir tous les utilisateurs")
async def get_users():
    users = await Get_all_utilisateurs()
    return {"utilisateurs": users}


# lister par role
@router.get("/role", summary="Obtenir les utilisateurs par rôle")
async def get_users_by_role(role: Role = Query(..., description="Rôle de l'utilisateur (admin, user)")):
    try:
        users = await Get_utilisateurs_by_role(role.value)
        return {"utilisateurs": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")


# Lister par type d'offre (premium/freemium) et par rôle
@router.get("/filter", summary="Lister les utilisateurs par type d'offre (premium/freemium) et par rôle")
async def get_users_by_role_and_offer(
    role: Role = Query(..., description="Rôle de l'utilisateur (admin ou user)"),
    ispremium: bool = Query(..., description="Statut premium (true ou false)")
):
    try:
        utilisateurs = await Get_utilisateurs_by_ispremium_and_role(role, ispremium)
        return {"utilisateurs": utilisateurs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")


# Un utilisateur par ID
@router.get("/{user_id}",summary="Obtenir un utilisateur par ID")
async def get_user_by_id(user_id: str):
    user = await Get_utilisateur_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return {"utilisateur": user}


# Liste par type d'offre (premium / freemium)
@router.get("/premium/{ispremium}",summary="Lister les utilisateurs par type d'offre (premium / freemium)")
async def get_users_by_offer(ispremium: bool):
    return await Get_utilisateurs_by_ispremium(ispremium)



# Changer le statut premium d’un utilisateur
@router.patch("/{user_id}/premium",summary="Changer le statut premium d’un utilisateur")
async def update_user_premium_status(utilisateur_id: str, ispremium: bool):
    return await Change_utilisateur_ispremium_status(utilisateur_id, ispremium)



#UPDATE
@router.put("/{user_id}", summary="Mettre à jour un utilisateur par ID")
async def update_user(user_id: str, user: dict):
    updated_user = await Update_utilisateur(user_id, user)
    return {"message": "Utilisateur mis à jour avec succès", "utilisateur": updated_user}

#DELETE
@router.delete("/{user_id}",summary="Supprimer un utilisateur par ID")
async def delete_user(user_id: str):
    deleted = await Delete_utilisateur(user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return {"message": "Utilisateur supprimé avec succès"}

