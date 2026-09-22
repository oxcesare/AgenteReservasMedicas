"""Pydantic Schemas"""
from .appointment import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from .availability import AvailabilitySlot, DoctorAvailabilityResponse
from .slot_create import (
    CreateAvailabilityRequest,
    SlotCreatedResponse,
    DayAvailability,
    TimeSlot,
    SlotUpdateRequest,
    SlotDetailResponse,
)
from .cita import (
    PacienteInput,
    CitaCreateRequest,
    CitaUpdateRequest,
    CitaPacienteResponse,
    CitaSlotResponse,
    CitaResponse,
)

__all__ = [
    "AppointmentCreate",
    "AppointmentUpdate",
    "AppointmentResponse",
    "AvailabilitySlot",
    "DoctorAvailabilityResponse",
    "CreateAvailabilityRequest",
    "SlotCreatedResponse",
    "DayAvailability",
    "TimeSlot",
    "SlotUpdateRequest",
    "SlotDetailResponse",
    "PacienteInput",
    "CitaCreateRequest",
    "CitaUpdateRequest",
    "CitaPacienteResponse",
    "CitaSlotResponse",
    "CitaResponse",
]
