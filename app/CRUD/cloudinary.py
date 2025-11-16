import os
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

load_dotenv()

# Config Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

def upload_to_cloudinary(file_bytes: bytes, folder="uploads", filename=None):
    """
    Upload d'un fichier vers Cloudinary.
    Les fichiers HTML/PDF/TXT => raw
    Les images => image (ou auto)
    """
    try:
        if not filename:
            filename = "file"

        ext = filename.split('.')[-1].lower()
        # Déterminer resource_type selon l'extension
        if ext in ["html", "pdf", "txt"]:
            resource_type = "raw"
        else:
            resource_type = "auto"  

        result = cloudinary.uploader.upload(
            file=(filename, file_bytes),
            folder=folder,
            resource_type=resource_type,
            use_filename=True,
            unique_filename=True,
            overwrite=False
        )

        # Créer raw_link pour les fichiers "raw"
        if resource_type == "raw":
            # raw_link = f"https://res.cloudinary.com/{os.getenv('CLOUDINARY_CLOUD_NAME')}/raw/upload/{result['public_id']}.{ext}"
            # Assurer que public_id ne contient pas l'extension
            public_id = result['public_id']
            if public_id.endswith(f".{ext}"):
                raw_link = f"https://res.cloudinary.com/{os.getenv('CLOUDINARY_CLOUD_NAME')}/raw/upload/{public_id}"
            else:
                raw_link = f"https://res.cloudinary.com/{os.getenv('CLOUDINARY_CLOUD_NAME')}/raw/upload/{public_id}.{ext}"

        else:
            raw_link = result.get("secure_url")

        return {
            "public_id": result.get("public_id"),
            "secure_url": result.get("secure_url"),
            "resource_type": result.get("resource_type"),
            "raw_link": raw_link,
            "raw": result
        }

    except Exception as e:
        raise Exception(f"Cloudinary upload failed: {e}")
