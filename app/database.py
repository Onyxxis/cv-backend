import motor.motor_asyncio
import os
from app.config import settings
from dotenv import load_dotenv

load_dotenv()

MONGO_DETAILS = os.getenv("MONGO_URI", "mongodb://localhost:27017")   

client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGODB_URI)
database = client[settings.DB_NAME]

# collections
utilisateur_collection = database.get_collection("utilisateurs")
template_collection = database.get_collection("templates")
cv_collection = database.get_collection("cvs")





async def test_connection():
    try:
        await client.admin.command('ping')
        print("Connexion MongoDB établie avec succès !")
    except Exception as e:
        print("Erreur de connexion MongoDB :", e)
