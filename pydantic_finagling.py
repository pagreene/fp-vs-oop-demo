from typing import Dict

from astropy.units import get_physical_type, UnitBase, Unit, Quantity
from pydantic import BaseModel

# Density: for example "g/mL" or "lb/gallon"
density_type = get_physical_type("mass density")

# Specific Volume: for example "cups/ounce" or "L/kg". The inverse of mass density.
specific_volume_type = get_physical_type("specific volume")

# Mass: for example "g", "lb", "ounce"
mass_type = get_physical_type("mass")

# Volume: for example "L" or "cup".
volume_type = get_physical_type("volume")


def validate_unit(unit: UnitBase | str) -> UnitBase:
    if isinstance(unit, str):
        return Unit(unit)
    elif isinstance(unit, UnitBase):
        return unit
    else:
        raise ValueError(f'Invalid type for unit: "{type(unit)}".')


def validate_quantity(quantity: Quantity | Dict) -> Quantity:
    if isinstance(quantity, dict):
        try:
            return float(quantity["value"]) * Unit(quantity["unit"])
        except KeyError:
            raise ValueError(
                f'Could not parts quantity dict: "{quantity}". Expected something of the form "{{"value": <value>, "unit": <unit>}}"'
            )
    elif isinstance(quantity, Quantity):
        return quantity
    else:
        raise ValueError(f'Invalid type for quantity: "{type(quantity)}".')


class UnitfulBaseModel(BaseModel):
    class Config:
        allow_mutation = False
        arbitrary_types_allowed = True
        json_encoders = {
            UnitBase: lambda unit: unit.to_string(),
            Quantity: lambda quant: {
                "value": quant.value,
                "unit": quant.unit.to_string(),
            },
        }
