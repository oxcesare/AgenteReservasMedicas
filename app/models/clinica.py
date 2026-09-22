"""Clinica model."""
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func

from app.database import Base


class Clinica(Base):
    """Clinica entity based on table clinicas."""

    __tablename__ = "clinicas"

    id_clinica = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    direccion = Column(Text, nullable=False)
    telefono = Column(String(20), nullable=True)
    activo = Column(Boolean, nullable=False, default=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())
