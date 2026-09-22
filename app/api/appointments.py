"""Appointments API Routes"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.schemas import AppointmentCreate, AppointmentUpdate, AppointmentResponse
from app.services import AppointmentService

router = APIRouter(prefix="/api/appointments", tags=["appointments"])


@router.post("/", response_model=AppointmentResponse, status_code=201)
def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new appointment"""
    return AppointmentService.create_appointment(db, appointment)


@router.get("/{appointment_id}", response_model=AppointmentResponse)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Get appointment by ID"""
    db_appointment = AppointmentService.get_appointment(db, appointment_id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment


@router.get("/", response_model=list[AppointmentResponse])
def get_all_appointments(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get all appointments with pagination"""
    return AppointmentService.get_all_appointments(db, skip, limit)


@router.get("/patient/{patient_name}", response_model=list[AppointmentResponse])
def get_patient_appointments(
    patient_name: str,
    db: Session = Depends(get_db)
):
    """Get all appointments for a specific patient"""
    appointments = AppointmentService.get_appointments_by_patient(db, patient_name)
    if not appointments:
        raise HTTPException(status_code=404, detail="No appointments found for this patient")
    return appointments


@router.put("/{appointment_id}", response_model=AppointmentResponse)
def update_appointment(
    appointment_id: int,
    appointment_update: AppointmentUpdate,
    db: Session = Depends(get_db)
):
    """Update an appointment"""
    db_appointment = AppointmentService.update_appointment(db, appointment_id, appointment_update)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment


@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Cancel an appointment"""
    db_appointment = AppointmentService.cancel_appointment(db, appointment_id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment


@router.patch("/{appointment_id}/confirm", response_model=AppointmentResponse)
def confirm_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Confirm an appointment"""
    db_appointment = AppointmentService.confirm_appointment(db, appointment_id)
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment


@router.delete("/{appointment_id}", status_code=204)
def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
):
    """Delete an appointment"""
    success = AppointmentService.delete_appointment(db, appointment_id)
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found")
