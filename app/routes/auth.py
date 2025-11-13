from fastapi import APIRouter, Depends, HTTPException, status
from app.models.auth import  UserLogin, UserOut, Token
from app.CRUD.cruduser import Create_utilisateur, utilisateur_collection, utilisateur_helper
from app.auth.utils import hash_password, verify_password, create_access_token, decode_access_token
from bson import ObjectId
import logging


router = APIRouter(
    prefix="/auth",
    tags=["authentification"]
)

 
logger = logging.getLogger("uvicorn.error")


@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    try:
        db_user = await utilisateur_collection.find_one({"email": user.email})
        if not db_user:
            raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
        try:
            if not verify_password(user.password, db_user["password"]):
                raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
        except Exception as e:
            logger.error(f"Erreur de vérification mot de passe pour {user.email}: {e}")
            raise HTTPException(status_code=500, detail="Erreur interne lors de la vérification du mot de passe")
        token_data = {
            "user_id": str(db_user["_id"]),
            "username": db_user.get("username", ""),
            "email": db_user["email"],
            "role": str(db_user.get("role", "user")),
            "ispremium": bool(db_user.get("ispremium", False))
        }
        try:
            access_token = create_access_token(token_data)
        except Exception as e:
            logger.error(f"Erreur création token JWT pour {user.email}: {e}")
            raise HTTPException(status_code=500, detail="Erreur interne lors de la création du token")
        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Erreur login inattendue pour {user.email}: {e}")
        raise HTTPException(status_code=500, detail="Erreur serveur inattendue")