"""HistorialCita model."""
from sqlalchemy import BigInteger, Column, DateTime, Enum, ForeignKey, String, func

from app.database import Base

ESTADOS_CITA = ("PROGRAMADA", "CONFIRMADA", "COMPLETADA", "CANCELADA", "NO_ASISTIO")


class HistorialCita(Base):
    """Appointment history entity based on table historial_citas."""

    __tablename__ = "historial_citas"

    id_historial = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    id_cita = Column(
        BigInteger,
        ForeignKey("citas.id_cita", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    estado_anterior = Column(Enum(*ESTADOS_CITA, name="estado_anterior_enum"), nullable=True)
    estado_nuevo = Column(Enum(*ESTADOS_CITA, name="estado_nuevo_enum"), nullable=False)
    cambiado_por = Column(
        Enum("PACIENTE_BOT", "DOCTOR_UI", "SISTEMA", name="cambiado_por_enum"),
        nullable=False,
    )
    comentario = Column(String(255), nullable=True)
    fecha_registro = Column(DateTime, nullable=False, server_default=func.now())
