from datetime import date
from typing import List, Optional

import jwt
from app.database.database import get_db
from app.models.reservation import Recurso, Reservation  # Importar modelos
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

router = APIRouter(prefix="/reservations", tags=["Reservations"])
security_bearer = HTTPBearer()


def get_user_id_from_credentials(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
) -> int:
    try:
        token = credentials.credentials
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub") or payload.get("id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: No se encuentra la identificación del usuario",
            )
        return int(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de autenticación inválidas",
        )


# ------------------------------------------------------------------
# SCHEMAS
# ------------------------------------------------------------------
class RecursoResponse(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True


class ReservationCreate(BaseModel):
    nombre_completo: str
    email: EmailStr
    fecha: date
    hora: str
    notas: Optional[str] = None
    recurso_id: Optional[int] = None


class ReservationResponse(BaseModel):
    id: int
    nombre_completo: str
    email: EmailStr
    fecha: date
    hora: str
    notas: Optional[str]
    user_id: Optional[int]
    recurso_id: Optional[int]
    recurso: Optional[RecursoResponse] = None

    class Config:
        from_attributes = True


# ------------------------------------------------------------------
# ENDPOINTS DE RECURSOS
# ------------------------------------------------------------------


@router.get("/recursos", response_model=List[RecursoResponse])
def get_recursos(db: Session = Depends(get_db)):
    """Devuelve la lista de recursos disponibles para que el frontend los despliegue."""
    lista = db.query(Recurso).all()
    if not lista:
        recursos_defecto = ["Gimnasio", "Cita Médica", "Oficina"]
        for nombre in recursos_defecto:
            db.add(Recurso(nombre=nombre))
        db.commit()
        lista = db.query(Recurso).all()
    return lista


# ------------------------------------------------------------------
# ENDPOINTS DE RESERVAS
# ------------------------------------------------------------------


@router.post(
    "/", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED
)
def create_reservation(
    reservation_data: ReservationCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_user_id_from_credentials),
):
    """Registra una reserva asociando el recurso seleccionado por el usuario."""

    if reservation_data.recurso_id:
        recurso_existe = (
            db.query(Recurso).filter(Recurso.id == reservation_data.recurso_id).first()
        )
        if not recurso_existe:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El recurso seleccionado no es válido",
            )

    nueva_reserva = Reservation(
        nombre_completo=reservation_data.nombre_completo,
        email=reservation_data.email,
        fecha=reservation_data.fecha,
        hora=reservation_data.hora,
        notas=reservation_data.notas,
        user_id=current_user_id,
        recurso_id=reservation_data.recurso_id,
    )

    db.add(nueva_reserva)
    db.commit()
    db.refresh(nueva_reserva)
    return nueva_reserva


@router.get("/", response_model=List[ReservationResponse])
def get_reservations(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_user_id_from_credentials),
):
    """Obtiene las reservas asociadas al usuario autenticado incluyendo sus recursos."""
    return db.query(Reservation).filter(Reservation.user_id == current_user_id).all()


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_user_id_from_credentials),
):
    """Elimina una reserva verificando propiedad."""
    reserva = (
        db.query(Reservation)
        .filter(
            Reservation.id == reservation_id, Reservation.user_id == current_user_id
        )
        .first()
    )

    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada o sin permisos",
        )

    db.delete(reserva)
    db.commit()
    return None
