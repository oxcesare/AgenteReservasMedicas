"""Appointment Service - Business Logic"""
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import Appointment
from app.schemas import AppointmentCreate, AppointmentUpdate
from app.models.appointment import AppointmentStatus


class AppointmentService:
    """Service for managing appointments"""
    
    @staticmethod
    def create_appointment(db: Session, appointment_data: AppointmentCreate) -> Appointment:
        """Create a new appointment"""
        db_appointment = Appointment(**appointment_data.dict())
        db.add(db_appointment)
        db.commit()
        db.refresh(db_appointment)
        return db_appointment
    
    @staticmethod
    def get_appointment(db: Session, appointment_id: int) -> Appointment:
        """Get appointment by ID"""
        return db.query(Appointment).filter(Appointment.id == appointment_id).first()
    
    @staticmethod
    def get_all_appointments(db: Session, skip: int = 0, limit: int = 10) -> list:
        """Get all appointments with pagination"""
        return db.query(Appointment).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_appointments_by_patient(db: Session, patient_name: str) -> list:
        """Get all appointments for a specific patient"""
        return db.query(Appointment).filter(
            Appointment.patient_name.ilike(f"%{patient_name}%")
        ).all()
    
    @staticmethod
    def get_appointments_by_date(db: Session, start_date: datetime, end_date: datetime) -> list:
        """Get appointments within a date range"""
        return db.query(Appointment).filter(
            Appointment.appointment_date.between(start_date, end_date)
        ).all()
    
    @staticmethod
    def update_appointment(
        db: Session,
        appointment_id: int,
        appointment_data: AppointmentUpdate
    ) -> Appointment:
        """Update an appointment"""
        db_appointment = AppointmentService.get_appointment(db, appointment_id)
        if db_appointment:
            update_data = appointment_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_appointment, key, value)
            db.commit()
            db.refresh(db_appointment)
        return db_appointment
    
    @staticmethod
    def cancel_appointment(db: Session, appointment_id: int) -> Appointment:
        """Cancel an appointment"""
        db_appointment = AppointmentService.get_appointment(db, appointment_id)
        if db_appointment:
            db_appointment.status = AppointmentStatus.CANCELLED
            db.commit()
            db.refresh(db_appointment)
        return db_appointment
    
    @staticmethod
    def confirm_appointment(db: Session, appointment_id: int) -> Appointment:
        """Confirm an appointment"""
        db_appointment = AppointmentService.get_appointment(db, appointment_id)
        if db_appointment:
            db_appointment.status = AppointmentStatus.CONFIRMED
            db.commit()
            db.refresh(db_appointment)
        return db_appointment
    
    @staticmethod
    def delete_appointment(db: Session, appointment_id: int) -> bool:
        """Delete an appointment"""
        db_appointment = AppointmentService.get_appointment(db, appointment_id)
        if db_appointment:
            db.delete(db_appointment)
            db.commit()
            return True
        return False
