import re  # 🌟 Esencial para la validación de formato de hora
from pathlib import Path

from app.database.database import Base, engine, get_db

# Importamos todos los modelos relacionales
from app.models.reservation import (  # 🌟 Modelos unificados
    Horario,
    Recurso,
    Reservation,
)
from app.models.user import User
from app.routes import reservations
from fastapi import (  # 🌟 Form permite capturar los envíos de Bootstrap
    Depends,
    FastAPI,
    Form,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

# Inicializar y sincronizar las tablas de la base de datos de forma automática
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Reservation Microservice")

# Configuración de CORS estricta para la comunicación sin bloqueos con React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar el motor de renderizado de vistas para el Administrador
templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent.parent / "templates")
)

# Incluir las rutas asíncronas de la API de reservas original
app.include_router(reservations.router)


# =====================================================================
# VISTAS Y ACCIONES DEL ADMINISTRADOR (PANEL HTML JINJA2)
# =====================================================================


@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request, db: Session = Depends(get_db)):
    users_list = db.query(User).all()
    reservations_list = db.query(Reservation).all()
    recursos_list = db.query(Recurso).all()  # 🌟 Carga los recursos creados
    horarios_list = (
        db.query(Horario).order_by(Horario.hora.asc()).all()
    )  # 🌟 Carga los bloques horarios ordenados

    # Renderizar inyectando todas las listas requeridas por la interfaz admin.html
    html_content = templates.get_template("admin.html").render(
        request=request,
        users=users_list,
        reservations=reservations_list,
        recursos=recursos_list,
        horarios=horarios_list,
    )
    return HTMLResponse(content=html_content)


@app.post("/admin/users/{user_id}/delete")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        # Cascade manual: eliminamos primero sus reservas asignadas para evitar errores de llave foránea
        db.query(Reservation).filter(Reservation.user_id == user_id).delete()
        db.delete(user)
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)


@app.post("/admin/reservations/{reservation_id}/delete")
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if reservation:
        db.delete(reservation)
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)


# 🌟 SOLUCIÓN 404: Ruta exacta receptora del formulario de creación de recursos
@app.post("/admin/recursos/create")
def create_recurso(nombre: str = Form(...), db: Session = Depends(get_db)):
    nombre_limpio = nombre.strip()
    if nombre_limpio:
        # Validamos duplicados del recurso para mantener la consistencia
        existe = db.query(Recurso).filter(Recurso.nombre == nombre_limpio).first()
        if not existe:
            nuevo_recurso = Recurso(nombre=nombre_limpio)
            db.add(nuevo_recurso)
            db.commit()
    return RedirectResponse(url="/admin", status_code=303)


# 🌟 SOLUCIÓN 404: Ruta exacta receptora del botón de eliminación de recursos
@app.post("/admin/recursos/{recurso_id}/delete")
def delete_recurso(recurso_id: int, db: Session = Depends(get_db)):
    recurso = db.query(Recurso).filter(Recurso.id == recurso_id).first()
    if recurso:
        # Primero desvinculamos o eliminamos las reservas asociadas a este recurso específico
        db.query(Reservation).filter(Reservation.recurso_id == recurso_id).delete()
        db.delete(recurso)
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)


# 🌟 VALIDACIÓN DE HORARIOS: Ruta que evita strings e ingresos basura en la hora
@app.post("/admin/horarios/create")
def create_horario(hora: str = Form(...), db: Session = Depends(get_db)):
    hora_limpia = hora.strip()

    # Expresión regular para validar formato estricto de reloj de 24 horas (HH:MM)
    patron_24h = r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$"

    if not re.match(patron_24h, hora_limpia):
        # Si introducen texto inválido salta la operación sin registrar en la BD
        return RedirectResponse(url="/admin", status_code=303)

    existe = db.query(Horario).filter(Horario.hora == hora_limpia).first()
    if not existe:
        nuevo_horario = Horario(hora=hora_limpia)
        db.add(nuevo_horario)
        db.commit()

    return RedirectResponse(url="/admin", status_code=303)


@app.post("/admin/horarios/{horario_id}/delete")
def delete_horario(horario_id: int, db: Session = Depends(get_db)):
    horario = db.query(Horario).filter(Horario.id == horario_id).first()
    if horario:
        db.delete(horario)
        db.commit()
    return RedirectResponse(url="/admin", status_code=303)


# =====================================================================
# ENDPOINTS API REQUERIDOS POR EL FRONTEND (REACT)
# =====================================================================


@app.get("/reservations/horarios")
def get_api_horarios(db: Session = Depends(get_db)):
    # Retorna los horarios en orden cronológico ascendente a React
    return db.query(Horario).order_by(Horario.hora.asc()).all()


# =====================================================================
# RUTA CONTROL DE RAÍZ
# =====================================================================


@app.get("/")
def read_root():
    return {"message": "Microservicio de Reservas Activo y Sincronizado"}
