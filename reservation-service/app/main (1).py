from app.database.database import Base, engine, get_db

# Importamos los modelos correspondientes
from app.models.reservation import Reservation
from app.models.user import User  # Ya tienes copiado user.py aquí
from app.routes import reservations
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

# Inicializar la base de datos
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Reservation Microservice")

# Configuración de CORS para comunicar con React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurar la ruta de las plantillas HTML
templates = Jinja2Templates(directory="templates")

# Incluir las rutas de gestión de reservas originales
app.include_router(reservations.router)


# =====================================================================
# VISTAS Y ACCIONES DEL ADMINISTRADOR (PANEL INTEGRADO RELACIONAL)
# =====================================================================


@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request, db: Session = Depends(get_db)):
    users_list = db.query(User).all()
    reservations_list = db.query(Reservation).all()

    # Renderizado directo usando el motor nativo de Jinja2 para evitar errores de versión
    html_content = templates.get_template("admin.html").render(
        request=request, users=users_list, reservations=reservations_list
    )
    return HTMLResponse(content=html_content)


@app.post("/admin/users/{user_id}/delete")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        # 🚀 Gracias a la relación, eliminamos primero sus reservas y luego al usuario
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


# =====================================================================
# RUTA RAÍZ
# =====================================================================


@app.get("/")
def read_root():
    return {"message": "Microservicio de Reservas Activo"}
