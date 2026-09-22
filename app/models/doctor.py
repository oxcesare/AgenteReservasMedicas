"""Doctor model."""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, func

from app.database import Base


class Doctor(Base):
    """Doctor entity based on table doctores."""

    __tablename__ = "doctores"

    id_doctor = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)
    apellido = Column(String(50), nullable=False)
    especialidad = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    telefono = Column(String(20), nullable=True)
    activo = Column(Boolean, nullable=False, default=True)
    creado_en = Column(DateTime, nullable=False, server_default=func.now())

