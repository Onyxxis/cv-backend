from fastapi import APIRouter, HTTPException, Query, UploadFile
from typing import List, Optional
from app.CRUD.crudcv import create_cv, get_all_cvs, get_completed_cvs_by_user, get_cv_by_id, get_cv_process_by_user, get_in_progress_cvs_by_user, update_cv, delete_cv, get_cvs_by_user,get_last_cv_by_user, get_recent_cvs_crud
from app.models.cv import CV

router = APIRouter(
    prefix="/cvs",
    tags=["CVs"]
)

# Créer un CV
@router.post("/", summary="Créer un CV")
async def create_cv_route(cv: CV):
    try:
        new_cv = await create_cv(cv.dict())
        return {"message": "CV créé avec succès", "cv": new_cv}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# Obtenir tous les CVs
@router.get("/", summary="Obtenir tous les CVs")
async def get_all_cvs_route():
    try:
        cvs = await get_all_cvs()
        return {"total": len(cvs), "cvs": cvs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@router.get("/count", summary="Obtenir le nombre total de CVs")
async def get_total_cvs():
    try:
        cvs = await get_all_cvs()
        total_cvs = len(cvs)
        return {"total_cvs": total_cvs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")


# --- derniers CVs générés ---
@router.get("/recent", summary="Obtenir les 4 derniers CVs générés", response_model=List[CV])
async def get_recent_cvs(limit: int = 4):
    try:
        recent_cvs = await get_recent_cvs_crud(limit)
        return recent_cvs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")
    

# Obtenir le nombre de CVs par tranche de complétion
@router.get("/stats/completion_tranches", summary="Obtenir le nombre de CVs par tranche de complétion")
async def get_completion_tranches():
    try:
        cvs = await get_all_cvs()   
        tranches = {
            "0-25": 0,
            "26-50": 0,
            "51-75": 0,
            "76-100": 0
        }

        for cv in cvs:
            percent = cv.get("completion_percentage", 0)
            if percent <= 25:
                tranches["0-25"] += 1
            elif percent <= 50:
                tranches["26-50"] += 1
            elif percent <= 75:
                tranches["51-75"] += 1
            else:
                tranches["76-100"] += 1

        return tranches

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur serveur : {str(e)}")


# Obtenir un CV par son ID
@router.get("/{cv_id}", summary="Obtenir un CV par ID")
async def get_cv_by_id_route(cv_id: str):
    try:
        cv = await get_cv_by_id(cv_id)
        return cv
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Mettre à jour un CV
@router.patch("/{cv_id}", summary="Mettre à jour un CV")
async def update_cv_route(cv_id: str, data: dict):
    try:
        updated_cv = await update_cv(cv_id, data)
        return {"message": "CV mis à jour avec succès", "cv": updated_cv}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Supprimer un CV
@router.delete("/{cv_id}", summary="Supprimer un CV")
async def delete_cv_route(cv_id: str):
    try:
        result = await delete_cv(cv_id)
        return result
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Obtenir tous les CVs d'un utilisateur
@router.get("/user/{user_id}", summary="Obtenir tous les CVs d'un utilisateur")
async def get_cvs_by_user_route(user_id: str):
    try:
        cvs = await get_cvs_by_user(user_id)
        return {"total": len(cvs), "cvs": cvs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# obtenir le dernier cv d'un utilisateur 
@router.get("/users/{user_id}/last", response_model=dict,summary="obtenir le dernier cv d'un utilisateur ")
async def get_last_cv(user_id: str):
    return await get_last_cv_by_user(user_id)


# obtenir la liste des cv complet 
@router.get("/user/{user_id}/completed",summary="obtenir la liste des cv complet")
async def get_completed_cvs(user_id: str):
    return {
        "status": "success",
        "cvs": await get_completed_cvs_by_user(user_id)
    }


@router.get("/user/{user_id}/in-progress",summary="obtenir la liste des cv non  complet")
async def get_in_progress_cvs(user_id: str):
    return {
        "status": "success",
        "cvs": await get_in_progress_cvs_by_user(user_id)
    }



@router.get("/in-progress/{user_id}",summary="pour avoir le nombre total  de cv complet et non complet ")
async def get_cv_stats(user_id: str):
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required")
    return await get_cv_process_by_user(user_id)




    

# Extraire les informations d'un CV à partir d'un fichier PDF
# @router.post("/upload-cv", summary="Extraire les informations d'un CV à partir d'un")
# async def upload_cv_route(file: UploadFile):
#     try:
#         extracted_cv = await extract_cv_from_pdf(file)
#         return {"message": "Extraction réussie", "cv": extracted_cv}
#     except HTTPException as http_exc:
#         raise http_exc
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))