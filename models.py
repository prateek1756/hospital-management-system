"""
Data models for Hospital Management System
Contains class definitions for Patient, Staff, Appointment, and Billing
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid

class Patient:
    """Patient model for storing patient information"""
    
    def __init__(self, name: str, age: int, gender: str, contact: str, 
                 medical_history: str = "", patient_id: Optional[str] = None):
        self.id = patient_id or str(uuid.uuid4())
        self.name = name
        self.age = age
        self.gender = gender
        self.contact = contact
        self.medical_history = medical_history
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert patient object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'contact': self.contact,
            'medical_history': self.medical_history,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Patient':
        """Create patient object from dictionary"""
        patient = cls(
            name=data['name'],
            age=data['age'],
            gender=data['gender'],
            contact=data['contact'],
            medical_history=data.get('medical_history', ''),
            patient_id=data['id']
        )
        patient.created_at = data.get('created_at', datetime.now().isoformat())
        patient.updated_at = data.get('updated_at', datetime.now().isoformat())
        return patient
    
    def __str__(self) -> str:
        return f"Patient(ID: {self.id}, Name: {self.name}, Age: {self.age}, Contact: {self.contact})"
    
    def __repr__(self) -> str:
        return self.__str__()

class Staff:
    """Staff model for storing hospital staff information"""
    
    def __init__(self, name: str, role: str, contact: str, 
                 specialization: str = "", staff_id: Optional[str] = None):
        self.id = staff_id or str(uuid.uuid4())
        self.name = name
        self.role = role  # doctor, nurse, admin
        self.contact = contact
        self.specialization = specialization
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert staff object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'contact': self.contact,
            'specialization': self.specialization,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Staff':
        """Create staff object from dictionary"""
        staff = cls(
            name=data['name'],
            role=data['role'],
            contact=data['contact'],
            specialization=data.get('specialization', ''),
            staff_id=data['id']
        )
        staff.created_at = data.get('created_at', datetime.now().isoformat())
        staff.updated_at = data.get('updated_at', datetime.now().isoformat())
        return staff
    
    def __str__(self) -> str:
        return f"Staff(ID: {self.id}, Name: {self.name}, Role: {self.role}, Contact: {self.contact})"
    
    def __repr__(self) -> str:
        return self.__str__()

class Appointment:
    """Appointment model for storing appointment information"""
    
    def __init__(self, patient_id: str, doctor_id: str, date: str, time: str,
                 status: str = "scheduled", notes: str = "", appointment_id: Optional[str] = None):
        self.id = appointment_id or str(uuid.uuid4())
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.date = date
        self.time = time
        self.status = status  # scheduled, completed, cancelled
        self.notes = notes
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert appointment object to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'doctor_id': self.doctor_id,
            'date': self.date,
            'time': self.time,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Appointment':
        """Create appointment object from dictionary"""
        appointment = cls(
            patient_id=data['patient_id'],
            doctor_id=data['doctor_id'],
            date=data['date'],
            time=data['time'],
            status=data.get('status', 'scheduled'),
            notes=data.get('notes', ''),
            appointment_id=data['id']
        )
        appointment.created_at = data.get('created_at', datetime.now().isoformat())
        appointment.updated_at = data.get('updated_at', datetime.now().isoformat())
        return appointment
    
    def __str__(self) -> str:
        return f"Appointment(ID: {self.id}, Patient: {self.patient_id}, Doctor: {self.doctor_id}, Date: {self.date}, Time: {self.time})"
    
    def __repr__(self) -> str:
        return self.__str__()

class Billing:
    """Billing model for storing billing information"""
    
    def __init__(self, patient_id: str, amount: float, services: List[str],
                 status: str = "unpaid", billing_id: Optional[str] = None):
        self.id = billing_id or str(uuid.uuid4())
        self.patient_id = patient_id
        self.amount = amount
        self.services = services
        self.status = status  # paid, unpaid, partial
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.payment_date = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert billing object to dictionary"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'amount': self.amount,
            'services': self.services,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'payment_date': self.payment_date
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Billing':
        """Create billing object from dictionary"""
        billing = cls(
            patient_id=data['patient_id'],
            amount=data['amount'],
            services=data['services'],
            status=data.get('status', 'unpaid'),
            billing_id=data['id']
        )
        billing.created_at = data.get('created_at', datetime.now().isoformat())
        billing.updated_at = data.get('updated_at', datetime.now().isoformat())
        billing.payment_date = data.get('payment_date')
        return billing
    
    def __str__(self) -> str:
        return f"Billing(ID: {self.id}, Patient: {self.patient_id}, Amount: ${self.amount}, Status: {self.status})"
    
    def __repr__(self) -> str:
        return self.__str__()
