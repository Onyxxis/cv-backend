from app.models.User import Utilisateur 
from app.database import utilisateur_collection
from bson import ObjectId,errors
from app.auth.utils import hash_password, verify_password
from fastapi import HTTPException
from app.CRUD.email_service import send_welcome_email

def utilisateur_helper(utilisateur) -> dict:
    return {
        "id": str(utilisateur["_id"]),
        "username": utilisateur["username"],
        "email": utilisateur["email"],
        "role": utilisateur["role"],
        "ispremium": utilisateur.get("ispremium", False)  
    }


# async def Create_utilisateur(utilisateur_data: dict) -> dict:
#     if utilisateur_data.get("role") == "admin":
#         utilisateur_data["ispremium"] = False
#     if "password" in utilisateur_data:
#         utilisateur_data["password"] = hash_password(utilisateur_data["password"])
#     result = await utilisateur_collection.insert_one(utilisateur_data)
#     new_utilisateur = await utilisateur_collection.find_one({"_id": result.inserted_id})
#     return utilisateur_helper(new_utilisateur)
async def Create_utilisateur(utilisateur_data: dict) -> dict:
    if utilisateur_data.get("role") == "admin":
        utilisateur_data["ispremium"] = False
    if "password" in utilisateur_data:
        utilisateur_data["password"] = hash_password(utilisateur_data["password"])
    result = await utilisateur_collection.insert_one(utilisateur_data)
    new_utilisateur = await utilisateur_collection.find_one({"_id": result.inserted_id})
    user = utilisateur_helper(new_utilisateur)
    try:
        send_welcome_email(
            to_email=user["email"],
            username=user["username"]
        )
    except Exception as e:
        print("Erreur lors de l'envoi de l'email :", e)

    return user




# Obtenir tous les utilisateurs 
async def Get_all_utilisateurs():
    utilisateurs = []
    async for utilisateur in utilisateur_collection.find():
        utilisateurs.append(utilisateur_helper(utilisateur))
    return utilisateurs


#  obtenir un utilisateur par ID
async def Get_utilisateur_by_id(utilisateur_id: str):
    utilisateur = await utilisateur_collection.find_one({"_id": ObjectId(utilisateur_id)})
    if utilisateur:
        return utilisateur_helper(utilisateur)


# UPDATE
async def Update_utilisateur(utilisateur_id: str, data: dict):
    try:
        obj_id = ObjectId(utilisateur_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID utilisateur invalide")
    if not data:
        raise HTTPException(status_code=400, detail="Aucun champ à mettre à jour")
    utilisateur = await utilisateur_collection.find_one({"_id": obj_id})
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    if utilisateur["role"] == "admin" and data.get("ispremium", False):
        raise HTTPException(status_code=400, detail="Les admins ne peuvent pas avoir ispremium à True")
    await utilisateur_collection.update_one({"_id": obj_id}, {"$set": data})
    updated_user = await utilisateur_collection.find_one({"_id": obj_id})
    return utilisateur_helper(updated_user)


# DELETE
async def Delete_utilisateur(utilisateur_id: str):
    utilisateur = await utilisateur_collection.find_one({"_id": ObjectId(utilisateur_id)})
    if utilisateur:
        await utilisateur_collection.delete_one({"_id": ObjectId(utilisateur_id)})
        return True
    return False


# liste par role
async def Get_utilisateurs_by_role(role: str):
    utilisateurs = []
    async for utilisateur in utilisateur_collection.find({"role": role}):
        utilisateurs.append(utilisateur_helper(utilisateur))
    return utilisateurs


# Lister les utilisateurs par type d'offre (premium / freemium)
async def Get_utilisateurs_by_ispremium(ispremium: bool):
    utilisateurs = []
    async for utilisateur in utilisateur_collection.find({"ispremium": ispremium}):
        utilisateurs.append(utilisateur_helper(utilisateur))
    return utilisateurs


# Changer le statut premium d’un utilisateur
async def Change_utilisateur_ispremium_status(utilisateur_id: str, ispremium: bool):
    try:
        object_id = ObjectId(utilisateur_id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="ID utilisateur invalide")
    utilisateur = await utilisateur_collection.find_one({"_id": object_id})
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    if utilisateur.get("role") == "admin" and ispremium:
        raise HTTPException(status_code=400, detail="Les administrateurs ne peuvent pas avoir ispremium=True")
    update_result = await utilisateur_collection.update_one(
        {"_id": object_id},
        {"$set": {"ispremium": ispremium}}
    )
    if update_result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Aucune modification effectuée")
    updated_user = await utilisateur_collection.find_one({"_id": object_id})
    return utilisateur_helper(updated_user)



# Lister par offre et par rôle
async def Get_utilisateurs_by_ispremium_and_role(role: str, ispremium: bool):
    filtre = {"role": role, "ispremium": ispremium}
    utilisateurs = []
    async for utilisateur in utilisateur_collection.find(filtre):
        utilisateurs.append(utilisateur_helper(utilisateur))
    return utilisateurs



async def Change_utilisateur_password(utilisateur_id: str, old_password: str, new_password: str) -> dict:
    """
    Vérifie l'ancien mot de passe et met à jour le nouveau mot de passe hashé.
    """
    try:
        obj_id = ObjectId(utilisateur_id)
    except errors.InvalidId:
        raise HTTPException(status_code=400, detail="ID utilisateur invalide")

    utilisateur = await utilisateur_collection.find_one({"_id": obj_id})
    if not utilisateur:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # Vérifier l'ancien mot de passe
    if not verify_password(old_password, utilisateur["password"]):
        raise HTTPException(status_code=400, detail="Ancien mot de passe incorrect")

    # Hash et mise à jour du nouveau mot de passe
    hashed_password = hash_password(new_password)
    await utilisateur_collection.update_one({"_id": obj_id}, {"$set": {"password": hashed_password}})

    updated_user = await utilisateur_collection.find_one({"_id": obj_id})
    return {
        "id": str(updated_user["_id"]),
        "username": updated_user["username"],
        "email": updated_user["email"],
        "role": updated_user["role"],
        "ispremium": updated_user.get("ispremium", False)
    }