from typing import Type

from app.schemas.vehicles import VehicleResponse
from app.models import Vehicle


def make_vehicle_response(vehicle: Type[Vehicle]) -> VehicleResponse:
    return VehicleResponse(
        vehicle_type=vehicle.vehicle_type,
        make=vehicle.make,
        model=vehicle.model,
        color=vehicle.color,
        year=vehicle.year,
        mileage=vehicle.mileage,
        vin=vehicle.vin,
        license_plate=vehicle.license_plate,
        registration_state=vehicle.registration_state,
        fuel_type=vehicle.fuel_type,
        transmission_type=vehicle.transmission_type,
        is_active=vehicle.is_active,
        nickname=vehicle.nickname,
        id=vehicle.id,
        created_at=vehicle.created_at,
        updated_at=vehicle.updated_at
    )
