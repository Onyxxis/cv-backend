from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt

# Configuration du hash
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Secrets JWT
SECRET_KEY = "secret_key"   
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 90  

# Hash et vérification du mot de passe
def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Le mot de passe est requis")
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    safe_password = password_bytes.decode("utf-8", errors="ignore")
    return pwd_context.hash(safe_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Création JWT
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Décoder JWT
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None
