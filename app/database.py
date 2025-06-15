# app/database.py
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session # Importa 'Session' aquí explícitamente
from sqlalchemy.sql import func
from databases import Database # Para conexiones asíncronas

# Importar configuración
from .config import settings

# --- Configuración de SQLAlchemy ---
# Asegúrate de que settings.DATABASE_URL esté configurado correctamente en config.py
# El pool_pre_ping es bueno para conexiones a DB en la nube
engine = create_engine(
    settings.DATABASE_URL.replace("asyncpg", "postgresql") # Adaptar URL para SQLAlchemy si es asyncpg
    .replace("pyodbc", "mssql+pyodbc"), # Adaptar URL para SQLAlchemy si es pyodbc
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Configuración de Bases para conexiones asíncronas (FastAPI) ---
# Usamos 'databases' para la capa asíncrona sobre SQLAlchemy
database = Database(settings.DATABASE_URL)

# --- Modelos ORM (SQLAlchemy) ---

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    role = Column(String, default="client", nullable=False) # 'client' o 'admin'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relación con Reservas (un usuario puede tener muchas reservas)
    reservations = relationship("Reservation", back_populates="owner")

class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(String, unique=True, index=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True) # Puede ser gestionado por reservas
    location = Column(String, nullable=True) # Ej: "interior", "terraza"

    # Relación con Reservas (una mesa puede tener muchas reservas)
    reservations = relationship("Reservation", back_populates="table_obj")


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)
    reservation_time = Column(DateTime(timezone=True), nullable=False)
    num_guests = Column(Integer, nullable=False)
    status = Column(String, default="pending", nullable=False) # 'pending', 'confirmed', 'cancelled'
    special_requests = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones para acceder a los objetos relacionados
    owner = relationship("User", back_populates="reservations")
    table_obj = relationship("Table", back_populates="reservations")

class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    discount_percentage = Column(Integer, nullable=True) # Ej: 10 para 10%
    code = Column(String, unique=True, nullable=True) # Código promocional

# --- Función para crear tablas ---
def create_db_tables():
    """Crea todas las tablas definidas en los modelos en la base de datos."""
    Base.metadata.create_all(bind=engine) # ¡Esta línea debe estar indentada aquí!

# --- Dependencia para obtener una sesión de DB ---
# Esta función generadora proporciona una sesión de base de datos SQLAlchemy
# y asegura que se cierre correctamente después de la solicitud.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()