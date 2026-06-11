from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr


class ReservationCreate(BaseModel):
    nombre_completo: str
    email: EmailStr
    fecha: date
    hora: str
    notas: Optional[str] = None


class ReservationResponse(ReservationCreate):
    id: int

    class Config:
        from_attributes = True
