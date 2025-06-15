# app/auth/security.py
from datetime import datetime, timedelta
from typing import Optional

from passlib.context import CryptContext
from jose import JWTError, jwt

# Importar configuración
from ..config import settings

# Contexto para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- Funciones de Hashing de Contraseñas ---

def verify_password(plain_password: str, hashed_password: str):
    """Verifica si una contraseña en texto plano coincide con una hasheada."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    """Genera el hash de una contraseña."""
    return pwd_context.hash(password)

# --- Funciones para JWT (JSON Web Tokens) ---

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crea un token de acceso JWT."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """Decodifica un token JWT y retorna su payload."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

# La dependencia OAuth2PasswordRequestForm se usa en routers, no aquí directamente.
# La dependencia OAuth2PasswordBearer se usa en crud, no aquí directamente.