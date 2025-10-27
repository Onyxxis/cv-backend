from fastapi import APIRouter, Depends, HTTPException, status
from app.models.auth import UserCreate, UserLogin, UserOut, Token
from app.CRUD.cruduser import Create_utilisateur, utilisateur_collection, utilisateur_helper
from app.auth.utils import hash_password, verify_password, create_access_token, decode_access_token
from bson import ObjectId

router = APIRouter(
    prefix="/auth",
    tags=["authentification"]
)

# Inscription
@router.post("/register", response_model=UserOut)
async def register(user: UserCreate):
    existing_user = await utilisateur_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email déjà utilisé")
    
    user_dict = user.dict()
    user_dict["password"] = hash_password(user_dict["password"])
    user_dict["role"] = "user"
    user_dict["ispremium"] = False

    new_user = await Create_utilisateur(user_dict)
    return new_user

# Connexion
@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    db_user = await utilisateur_collection.find_one({"email": user.email})
    if not db_user:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    
    token_data = {"user_id": str(db_user["_id"]), "email": db_user["email"], "role": db_user["role"]}
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}
