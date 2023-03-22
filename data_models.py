from typing import List

from astropy import units as u
from astropy.units import UnitBase, Quantity
from pydantic import validator

from pydantic_finagling import UnitfulBaseModel, density_type, mass_type, specific_volume_type, volume_type, \
    validate_unit, validate_quantity


class MaterialData(UnitfulBaseModel):
    """A known material with physical properties.

    The unit indicates the preferred unit representation for this material, and the
    mass_per_unit and volume_per_unit allow mass or volume measurements to be
    converted to the preferred unit.
    """
    name: str
    unit: UnitBase
    mass_per_unit: Quantity[density_type, mass_type] | None
    volume_per_unit: Quantity[specific_volume_type, volume_type] | None

    _validate_unit = validator("unit", pre=True, always=True, allow_reuse=True)(
        validate_unit
    )
    _validate_mass_per_unit = validator("mass_per_unit", pre=True, always=True, allow_reuse=True)(
        lambda q: None if q is None else validate_quantity(q)
    )
    _validate_volume_per_unit = validator("volume_per_unit", pre=True, always=True, allow_reuse=True)(
        lambda q: None if q is None else validate_quantity(q)
    )


class IngredientData(UnitfulBaseModel):
    """An item with a quantity and a name.

    The item names will be compared with the list of known materials. Although it is not
    required that a name match (feel free to use off-the-cuff ingredients), it is beneficial
    to ensure a match if you are in fact using a known material (don't just spell it wrong).
    """
    quantity: Quantity[mass_type, volume_type, u.count]
    item: str

    _validate_quantity = validator("quantity", pre=True, always=True, allow_reuse=True)(
        validate_quantity
    )


class RecipeData(UnitfulBaseModel):
    """A recipe with name, source, instructions, and ingredients."""
    name: str
    source: str
    ingredients: List[IngredientData]
    instructions: List[str]
