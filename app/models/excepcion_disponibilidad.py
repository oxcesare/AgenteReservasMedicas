"""ExcepcionDisponibilidad model."""
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.database import Base


class ExcepcionDisponibilidad(Base):
    """Availability exception entity based on table excepciones_disponibilidad."""

    __tablename__ = "excepciones_disponibilidad"

    id_excepcion = Column(Integer, primary_key=True, index=True)
    id_doctor = Column(Integer, ForeignKey("doctores.id_doctor"), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    motivo = Column(String(255), nullable=True)
