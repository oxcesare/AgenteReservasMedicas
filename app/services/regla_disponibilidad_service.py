"""Regla Disponibilidad service."""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.doctor import Doctor
from app.models.slot_disponibilidad import SlotDisponibilidad, SlotEstado
from app.schemas.availability import AvailabilitySlot, DoctorAvailabilityResponse


class ReglaDisponibilidadService:
    """ Lógica de negocio para Reglas de Disponibilidad ."""