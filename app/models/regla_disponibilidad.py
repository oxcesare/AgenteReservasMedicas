"""ReglaDisponibilidad model."""
from sqlalchemy import Column, Date, Enum, ForeignKey, Integer, SmallInteger, Time

from app.database import Base


class ReglaDisponibilidad(Base):
    """Availability rule entity based on table reglas_disponibilidad."""

    __tablename__ = "reglas_disponibilidad"

    id_regla = Column(Integer, primary_key=True, index=True)
    id_doctor = Column(Integer, ForeignKey("doctores.id_doctor"), nullable=False)
    id_clinica = Column(Integer, ForeignKey("clinicas.id_clinica"), nullable=False)
    tipo_recurrencia = Column(
        Enum(
            "DIARIA",
            "SEMANAL",
            "QUINCENAL",
            "MENSUAL",
            "FECHA_UNICA",
            name="tipo_recurrencia_enum",
        ),
        nullable=False,
    )
    # 1=Lunes, 7=Domingo (recurrencia semanal/quincenal)
    dia_semana = Column(SmallInteger, nullable=True)
    hora_inicio = Column(Time, nullable=False)
    hora_fin = Column(Time, nullable=False)
    duracion_slot_minutos = Column(Integer, nullable=True, default=30)
    fecha_inicio_validez = Column(Date, nullable=False)
    fecha_fin_validez = Column(Date, nullable=True)
