"""Schemas for doctor availability."""
from datetime import datetime

from pydantic import BaseModel


class AvailabilityCitaPaciente(BaseModel):
    id_paciente: int
    nombre: str
    apellido: str
    telefono_whatsapp: str
    email: str | None = None


class AvailabilityCita(BaseModel):
    id_cita: int
    estado_actual: str
    notas_paciente: str | None = None
    paciente: AvailabilityCitaPaciente


class AvailabilitySlot(BaseModel):
    id_slot: int
    id_clinica: int
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    estado: str
    cita: AvailabilityCita | None = None


class DoctorAvailabilityResponse(BaseModel):
    id_doctor: int
    desde: datetime
    hasta: datetime
    pagina: int
    tamano_pagina: int
    total_slots: int
    slots: list[AvailabilitySlot]
