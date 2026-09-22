"""Schemas for citas."""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class PacienteInput(BaseModel):
    """Patient data sent by the booking flow."""

    nombre: str = Field(..., max_length=50)
    apellido: str = Field(..., max_length=50)
    telefono_whatsapp: str = Field(..., max_length=20)
    email: EmailStr | None = None


class CitaCreateRequest(BaseModel):
    """Request to create an appointment."""

    id_slot: int
    paciente: PacienteInput
    notas_paciente: str | None = Field(default=None, max_length=255)


class CitaUpdateRequest(BaseModel):
    """Request to update an appointment."""

    id_slot: int | None = None
    notas_paciente: str | None = Field(default=None, max_length=255)
    estado_actual: str | None = Field(
        default=None,
        description="Nuevo estado de la cita: PROGRAMADA, CONFIRMADA, COMPLETADA, CANCELADA, NO_ASISTIO",
    )


class CitaPacienteResponse(BaseModel):
    id_paciente: int
    nombre: str
    apellido: str
    telefono_whatsapp: str
    email: str | None = None


class CitaSlotResponse(BaseModel):
    id_slot: int
    id_doctor: int
    id_clinica: int
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime


class CitaResponse(BaseModel):
    id_cita: int
    estado_actual: str
    notas_paciente: str | None = None
    creado_en: datetime
    paciente: CitaPacienteResponse
    slot: CitaSlotResponse
