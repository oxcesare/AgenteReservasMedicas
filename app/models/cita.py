"""Cita model."""
import enum

from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, Integer, String, func

from app.database import Base


class EstadoCita(str, enum.Enum):
    """Estados posibles de una cita."""

    PROGRAMADA = "PROGRAMADA"
    CONFIRMADA = "CONFIRMADA"
    COMPLETADA = "COMPLETADA"
    CANCELADA = "CANCELADA"
    NO_ASISTIO = "NO_ASISTIO"


class Cita(Base):
    """Cita entity based on table citas."""

    __tablename__ = "citas"

    id_cita = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    id_slot = Column(BigInteger, ForeignKey("slots_disponibilidad.id_slot"), unique=True, nullable=False)
    id_paciente = Column(Integer, ForeignKey("pacientes.id_paciente"), nullable=False, index=True)
    estado_actual = Column(Enum(EstadoCita), nullable=False, default=EstadoCita.PROGRAMADA)
    notas_paciente = Column(String(255), nullable=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
