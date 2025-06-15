# app/crud/user.py
from sqlalchemy.orm import Session
from ..database import User # Importamos la clase User directamente
from ..schemas import user as user_schemas
from ..auth import security
from fastapi import HTTPException, status, Depends # Asegúrate que Depends esté aquí
from jose import JWTError
from typing import Annotated # Necesaria para Annotated
from fastapi.security import OAuth2PasswordBearer # Necesaria para OAuth2PasswordBearer

# --- Definición de OAuth2 scheme (Debe ir aquí, a nivel global del módulo) ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")

# --- Operaciones de Lectura (GET) ---

def get_user(db: Session, user_id: int):
    """Obtiene un usuario por su ID."""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Obtiene un usuario por su email."""
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """Obtiene una lista de usuarios con paginación."""
    return db.query(User).offset(skip).limit(limit).all()

# --- Operaciones de Creación (POST) ---

def create_user(db: Session, user: user_schemas.UserCreate):
    """Crea un nuevo usuario con la contraseña hasheada."""
    hashed_password = security.get_password_hash(user.password)
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Operaciones de Actualización (PUT/PATCH) ---

def update_user(db: Session, user_id: int, user_update: user_schemas.UserUpdate):
    """Actualiza los datos de un usuario existente."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        update_data = user_update.model_dump(exclude_unset=True) # Usa model_dump para Pydantic V2
        for key, value in update_data.items():
            setattr(db_user, key, value)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    return db_user

# --- Operaciones de Eliminación (DELETE) ---

def delete_user(db: Session, user_id: int):
    """Elimina un usuario por su ID."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True # Indica que se eliminó con éxito
    return False # Indica que el usuario no fue encontrado

# --- Autenticación ---

def authenticate_user(db: Session, email: str, password: str):
    """Autentica un usuario verificando su email y contraseña."""
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not security.verify_password(password, user.hashed_password):
        return False
    return user

def get_current_active_user(
    db: Session,
    token: Annotated[str, Depends(oauth2_scheme)] # Aquí es donde se usa oauth2_scheme
) -> User: # Indica que devuelve un objeto User de SQLAlchemy
    """Obtiene el usuario activo a partir de un token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = security.decode_access_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = user_schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user