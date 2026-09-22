"""Paciente model."""
from sqlalchemy import Column, DateTime, Integer, String, func

from app.database import Base


class Paciente(Base):
    """Paciente entity based on table pacientes."""

    __tablename__ = "pacientes"

    id_paciente = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    telefono_whatsapp = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100), nullable=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
