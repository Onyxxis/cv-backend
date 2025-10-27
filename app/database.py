import motor.motor_asyncio
from app.config import settings



client = motor.motor_asyncio.AsyncIOMotorClient(
    settings.MONGODB_URI,
    tls=True,   
    tlsAllowInvalidCertificates=True   
)

database = client[settings.DB_NAME]

utilisateur_collection = database.get_collection("utilisateurs")
template_collection = database.get_collection("templates")
cv_collection = database.get_collection("cvs")



async def test_connection():
    try:
        await client.admin.command('ping')
        print("Connexion MongoDB établie avec succès !")
    except Exception as e:
        print("Erreur de connexion MongoDB :", e)
