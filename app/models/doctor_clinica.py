"""DoctorClinica model (M:N relation between doctores and clinicas)."""
from sqlalchemy import Column, ForeignKey, Integer

from app.database import Base


class DoctorClinica(Base):
    """Association entity based on table doctor_clinica."""

    __tablename__ = "doctor_clinica"

    id_doctor = Column(
        Integer,
        ForeignKey("doctores.id_doctor", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    id_clinica = Column(
        Integer,
        ForeignKey("clinicas.id_clinica", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
