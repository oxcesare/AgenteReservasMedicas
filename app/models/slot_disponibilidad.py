"""Slot disponibilidad model."""
import enum

from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, Integer

from app.database import Base


class SlotEstado(str, enum.Enum):
    """Estados del slot en BD."""

    DISPONIBLE = "DISPONIBLE"
    RESERVADO = "RESERVADO"
    BLOQUEADO = "BLOQUEADO"


class SlotDisponibilidad(Base):
    """Slot entity based on table slots_disponibilidad."""

    __tablename__ = "slots_disponibilidad"

    id_slot = Column(BigInteger, primary_key=True, index=True)
    id_doctor = Column(Integer, ForeignKey("doctores.id_doctor"), nullable=False, index=True)
    id_clinica = Column(Integer, ForeignKey("clinicas.id_clinica"), nullable=False)
    fecha_hora_inicio = Column(DateTime, nullable=False, index=True)
    fecha_hora_fin = Column(DateTime, nullable=False)
    estado = Column(Enum(SlotEstado), nullable=False, default=SlotEstado.DISPONIBLE)
