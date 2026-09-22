"""Appointment Model"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from app.database import Base
import enum


class AppointmentStatus(str, enum.Enum):
    """Appointment status enumeration"""
    PENDING = "pendiente"
    CONFIRMED = "confirmada"
    CANCELLED = "cancelada"
    COMPLETED = "completada"


class Appointment(Base):
    """Appointment database model"""
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_name = Column(String(100), nullable=False)
    patient_phone = Column(String(20), nullable=False)
    patient_email = Column(String(100), nullable=True)
    doctor_name = Column(String(100), nullable=False)
    specialty = Column(String(100), nullable=False)
    appointment_date = Column(DateTime, nullable=False)
    notes = Column(Text, nullable=True)
    status = Column(
        Enum(AppointmentStatus),
        default=AppointmentStatus.PENDING,
        nullable=False
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Appointment(id={self.id}, patient={self.patient_name}, doctor={self.doctor_name}, date={self.appointment_date})>"
