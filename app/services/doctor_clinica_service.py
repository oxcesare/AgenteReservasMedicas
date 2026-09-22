"""Doctor Clinica Serviceservice."""
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.doctor import Doctor
from app.models.slot_disponibilidad import SlotDisponibilidad, SlotEstado
from app.schemas.availability import AvailabilitySlot, DoctorAvailabilityResponse


class DoctorClinicaService:
    """ Lógica de negocio para Doctor Clinica ."""