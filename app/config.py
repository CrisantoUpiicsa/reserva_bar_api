# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class Settings(BaseSettings):
    # La URL de la base de datos se leerá de una variable de entorno
    # Si usas PostgreSQL: postgresql+asyncpg://user:password@localhost:5432/reserva_bar_db
    # Si usas Azure SQL Database (SQL Server): mssql+pyodbc://user:password@server.database.windows.net/db_name?driver=ODBC+Driver+17+for+SQL+Server
    DATABASE_URL: str = "sqlite:///./sql_app.db" # Usamos SQLite por defecto para desarrollo local fácil

    SECRET_KEY: str = "supersecretkey" # ¡CAMBIA ESTO EN PRODUCCIÓN! Usa una cadena aleatoria y compleja.
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Configuración para cargar variables de entorno desde un archivo .env
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()