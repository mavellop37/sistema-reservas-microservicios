from app.database.database import Base, engine
from app.routes import auth
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Inicializar la base de datos para crear la tabla de usuarios
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth & User Microservice")

# Dominios explícitamente permitidos para transferir credenciales de forma segura
origins = [
    "https://mar.origenet.cl",  # Tu dominio de producción en cPanel
    "http://localhost:5173",  # Tu entorno local de desarrollo con Vite
]

# Configuración de CORS corregida sin asterisco para dar soporte a credentials=True
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir únicamente las rutas de autenticación
app.include_router(auth.router)


@app.get("/")
def read_root():
    return {"message": "Microservicio de Autenticación Activo"}
