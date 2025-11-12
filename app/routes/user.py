from dataclasses import Field
from fastapi import APIRouter, HTTPException, Path, Query
from app.CRUD.cruduser import (
    Change_utilisateur_password,
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


# --- Nombre total d'utilisateurs ---
@router.get("/count", summary="Obtenir le nombre total d'utilisateurs")
async def get_total_users():
    try:
        utilisateurs = await Get_all_utilisateurs()
        total_users = len(utilisateurs)
        return {"total_utilisateurs": total_users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")



# Obtenir le nombre d'utilisateurs par rôle pour un pie chart
@router.get("/stats/roles", summary="Statistiques des utilisateurs par rôle")
async def get_users_count_by_role():
     
    try:
        users_admin = await Get_utilisateurs_by_role(Role.ADMIN.value)
        users_user = await Get_utilisateurs_by_role(Role.USER.value)

        data = [
            {"role": "Admin", "count": len(users_admin)},
            {"role": "User", "count": len(users_user)}
        ]
        return {"data": data}

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



class PasswordUpdate(BaseModel):
    oldPassword: str = Field(..., min_length=6)
    newPassword: str = Field(..., min_length=6)
    confirmPassword: str = Field(..., min_length=6)

@router.put("/{user_id}/password", summary="Modifier le mot de passe d'un utilisateur par ID")
async def update_password_by_id(
    user_id: str = Path(..., description="ID de l'utilisateur"),
    password_data: PasswordUpdate = ...,
):
    # Vérification confirmation
    if password_data.newPassword != password_data.confirmPassword:
        raise HTTPException(status_code=400, detail="La confirmation du mot de passe ne correspond pas")

    # Appel CRUD
    updated_user = await Change_utilisateur_password(
        utilisateur_id=user_id,
        old_password=password_data.oldPassword,
        new_password=password_data.newPassword
    )

    return {"message": "Mot de passe mis à jour avec succès", "utilisateur": updated_user}