"""Schemas for creating doctor availability slots."""
from datetime import date, datetime, time
from pydantic import BaseModel, Field


class TimeSlot(BaseModel):
    """Individual time slot (e.g., 7am-9am)"""
    hora_inicio: time = Field(..., description="Start time (HH:MM format)")
    hora_fin: time = Field(..., description="End time (HH:MM format)")


class DayAvailability(BaseModel):
    """Availability for a single day with multiple time slots"""
    fecha: date = Field(..., description="Date (YYYY-MM-DD format)")
    franjas: list[TimeSlot] = Field(..., description="List of time slots for this day")


class CreateAvailabilityRequest(BaseModel):
    """Request to create multiple availability slots"""
    id_doctor: int = Field(..., description="Doctor ID")
    id_clinica: int = Field(..., description="Clinic ID")
    slots: list[DayAvailability] = Field(
        ..., description="List of days with their time slots"
    )


class SlotCreatedResponse(BaseModel):
    """Response after creating slots"""
    id_doctor: int
    id_clinica: int
    total_slots_creados: int
    detalles: list[dict] = Field(default_factory=list)


class SlotUpdateRequest(BaseModel):
    """Request to update a single availability slot."""

    fecha: date = Field(..., description="Date (YYYY-MM-DD format)")
    hora_inicio: time = Field(..., description="Start time (HH:MM format)")
    hora_fin: time = Field(..., description="End time (HH:MM format)")
    id_clinica: int | None = Field(default=None, description="Clinic ID (optional)")


class SlotDetailResponse(BaseModel):
    """Response for a single slot."""

    id_slot: int
    id_doctor: int
    id_clinica: int
    fecha_hora_inicio: datetime
    fecha_hora_fin: datetime
    estado: str
