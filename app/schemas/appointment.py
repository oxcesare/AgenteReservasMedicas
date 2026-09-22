"""Appointment Schemas"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class AppointmentCreate(BaseModel):
    """Schema for creating an appointment"""
    patient_name: str
    patient_phone: str
    patient_email: Optional[EmailStr] = None
    doctor_name: str
    specialty: str
    appointment_date: datetime
    notes: Optional[str] = None


class AppointmentUpdate(BaseModel):
    """Schema for updating an appointment"""
    patient_name: Optional[str] = None
    patient_phone: Optional[str] = None
    patient_email: Optional[EmailStr] = None
    doctor_name: Optional[str] = None
    specialty: Optional[str] = None
    appointment_date: Optional[datetime] = None
    notes: Optional[str] = None
    status: Optional[str] = None


class AppointmentResponse(BaseModel):
    """Schema for appointment response"""
    id: int
    patient_name: str
    patient_phone: str
    patient_email: Optional[str] = None
    doctor_name: str
    specialty: str
    appointment_date: datetime
    notes: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
