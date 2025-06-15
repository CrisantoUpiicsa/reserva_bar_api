# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session # Asegúrate de importar Session aquí
from datetime import timedelta

# Importa los módulos necesarios
from . import crud, schemas # Mantenemos 'schemas' si se usa genéricamente en main.py
from .database import engine, SessionLocal, create_db_tables, database, Base # Importa Base también
from .auth import security # Importa tu módulo de seguridad con las funciones de autenticación
from .routers import users as users_router # Importa el router de usuarios

# Crea la instancia de la aplicación FastAPI
app = FastAPI(
    title="API de Reserva de Bar",
    description="API para la gestión de reservas de mesas, usuarios y promociones de un bar.",
    version="0.1.0",
)

# Incluye el router de usuarios
app.include_router(users_router.router) # Aquí se incluye el router que creamos

# Eventos de inicio y cierre de la aplicación para la conexión a la base de datos
@app.on_event("startup")
async def startup():
    print("Iniciando la aplicación y conectando a la base de datos...")
    await database.connect() # Conectar la base de datos asíncrona
    # La creación de tablas ahora se manejará a través del endpoint /users/create-db-tables/
    print("Conexión a la base de datos establecida.")

@app.on_event("shutdown")
async def shutdown():
    print("Cerrando la aplicación y desconectando de la base de datos...")
    await database.disconnect() # Desconectar la base de datos asíncrona
    print("Conexión a la base de datos cerrada.")

# Ruta raíz para verificar que la API está activa
@app.get("/")
async def read_root():
    return {"message": "API de Reserva de Bar funcionando"}