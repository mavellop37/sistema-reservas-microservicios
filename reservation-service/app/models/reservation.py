from app.database.database import Base
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Recurso(Base):
    __tablename__ = "recursos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, unique=True)

    # Relación inversa
    reservas = relationship("Reservation", back_populates="recurso")


# 🌟 CORREGIDO: Extraído fuera de Recurso con la identación correcta
class Horario(Base):
    __tablename__ = "horarios"

    id = Column(Integer, primary_key=True, index=True)
    hora = Column(String, unique=True, nullable=False)


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String, nullable=False)
    email = Column(String, nullable=False)
    fecha = Column(Date, nullable=False)
    hora = Column(String, nullable=False)
    notas = Column(String, nullable=True)
    user_id = Column(Integer, nullable=True)

    recurso_id = Column(Integer, ForeignKey("recursos.id"), nullable=True)

    recurso = relationship("Recurso", back_populates="reservas")
