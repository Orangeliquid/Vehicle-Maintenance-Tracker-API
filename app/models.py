from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)

    vehicles = relationship("Vehicle", back_populates="user", cascade="all, delete-orphan")


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    vehicle_type = Column(String)  # Sedan, Coupe, Motorcycle
    make = Column(String)  # Subaru, Toyota
    model = Column(String)  # Outback, Camry
    color = Column(String)  # Orange, White
    year = Column(Integer, index=True)  # 2024, 1999
    mileage = Column(Integer)  # 133150, 59800
    vin = Column(String, unique=True, nullable=False, index=True)  # 1F6A1234567890123, 4Y1SL65848Z411439
    license_plate = Column(String, unique=True, index=True)  # AZM9590, JGY-6201
    registration_state = Column(String, index=True)  # Ohio, Alabama
    fuel_type = Column(String)  # Gasoline, Electric, Diesel
    transmission_type = Column(String)  # Manual, Automatic
    is_active = Column(Boolean, index=True)  # True/False
    nickname = Column(String)  # Big Bertha

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="vehicles")

    maintenance_records = relationship(
        "MaintenanceRecord", back_populates="vehicle", cascade="all, delete-orphan"
    )

    maintenance_reminders = relationship(
        "MaintenanceReminder", back_populates="vehicle", cascade="all, delete-orphan"
    )


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), index=True)
    maintenance_provider = Column(String, index=True)  # Valvoline, Quick-I-Lube, Self
    maintenance_type = Column(String, index=True)  # Oil Change, Brake Replacement
    description = Column(String)  # Replaced brakes for all wheels, Emptied and replaced oil with synthetic grade oil
    mileage = Column(Integer)  # 133150, 59800
    cost = Column(Float)  # 1256.12, 165.00
    serviced_at = Column(DateTime(timezone=True), index=True, nullable=True)  # Date of service
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)  # Date of data entry
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), index=True)  # Date of last update

    vehicle = relationship("Vehicle", back_populates="maintenance_records")


class MaintenanceReminder(Base):
    __tablename__ = "maintenance_reminder"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), index=True)
    maintenance_type = Column(String, nullable=False)  # Oil-change, tire rotation
    details = Column(String, nullable=True)  # Oil-change required in 3k miles
    interval_miles = Column(Integer, nullable=True)  # 3000, 60000
    interval_months = Column(Integer, nullable=True)  # 6, 12
    last_serviced_mileage = Column(Integer, nullable=True)  # 45800, 68500
    last_serviced_date = Column(DateTime, nullable=True)  # Date of last service in datetime format
    notify_before_miles = Column(Integer, default=500)  # 300, 500
    notify_before_days = Column(Integer, default=14)  # 15, 30
    estimated_miles_driven_per_month = Column(Integer, default=500)  # default is less than average
    is_active = Column(Boolean, default=True)  # Bool
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Date created in datetime
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), index=True)  # Date updated in datetime

    vehicle = relationship("Vehicle", back_populates="maintenance_reminders")
