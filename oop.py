from typing import List, Iterable
from astropy import units as u

from data_models import MaterialData, IngredientData, load_list, RecipeData


class Material:
    def __init__(
            self,
            name: str,
            unit: u.UnitBase,
            mass_per_unit: u.Quantity = None,
            volume_per_unit: u.Quantity = None
    ):
        self.name = name
        self.unit = unit
        self._mass_per_unit = mass_per_unit
        self._volume_per_unit = volume_per_unit

    def __str__(self):
        return f"Material({self.name} [{self.unit}])"

    def regularize_physical_type(self, quantity):
        if quantity.unit.physical_type == u.get_physical_type("mass"):
            return quantity / self._mass_per_unit
        elif quantity.unit.physical_type == u.get_physical_type("volume"):
            return quantity / self._volume_per_unit
        else:
            raise ValueError(f"Cannot regularize {quantity} as {self}.")

    def regularize_unit(self, quantity):
        return quantity.to(self.unit)


class MaterialDefinitions:
    def __init__(self, material_list: Iterable[Material]):
        self._material_lookup = {material.name: material for material in material_list}

    @classmethod
    def from_file(cls, filename):
        material_data_list = (
            Material(**material_data.dict())
            for material_data in load_list(filename, MaterialData.parse_obj)
        )
        return cls(material_list=material_data_list)

    def load_ingredient(self, ingredient_data: IngredientData) -> "Ingredient":
        material = self._material_lookup.get(ingredient_data.item)

        if material:
            return Ingredient(quantity=ingredient_data.quantity, material=material)

        new_material = Material(name=ingredient_data.item, unit=ingredient_data.quantity.unit)
        self._material_lookup[new_material.name] = new_material

        return Ingredient(quantity=ingredient_data.quantity, material=new_material)


class Ingredient:
    def __init__(self, quantity: u.Quantity, material: Material):
        self.material = material

        if quantity.unit.physical_type == material.unit.physical_type:
            quantity = quantity
        else:
            quantity = material.regularize_physical_type(quantity)

        self.quantity = material.regularize_unit(quantity)


class Recipe:
    def __init__(
            self,
            name: str,
            source: str,
            ingredients: List[Ingredient],
            instructions: List[str]
    ):
        self.name = name
        self.source = source
        self.ingredients = ingredients
        self.instructions = instructions


class ShoppingCart:
    def __init__(
            self,
            recipes: List[Recipe],
            material_definitions: MaterialDefinitions
    ):
        self.recipes = recipes
        self._material_definitions = material_definitions
        self._shopping_cart = {}

    @classmethod
    def from_files(cls, recipes_file: str, materials_file: str) -> "ShoppingCart":
        material_definitions = MaterialDefinitions.from_file(materials_file)

        recipe_data_list = load_list(recipes_file, RecipeData.parse_obj)
        recipes = []
        for recipe_data in recipe_data_list:
            ingredient_list = [
                material_definitions.load_ingredient(ingredient_data)
                for ingredient_data in recipe_data.ingredients
            ]
            recipes.append(
                Recipe(
                    name=recipe_data.name,
                    source=recipe_data.source,
                    ingredients=ingredient_list,
                    instructions=recipe_data.instructions
                )
            )

        return cls(recipes, material_definitions)

    def get_shopping_list(self) -> List[Ingredient]:
        if not self._shopping_cart:
            for recipe in self.recipes:
                for ingredient in recipe.ingredients:
                    if ingredient.material.name not in self._shopping_cart:
                        self._shopping_cart[ingredient.material.name] = Ingredient(
                            quantity=0*ingredient.material.unit,
                            material=ingredient.material
                        )
                    self._shopping_cart[ingredient.material.name].quantity += ingredient.quantity
        return list(self._shopping_cart.values())


def main():
    shopping_cart = ShoppingCart.from_files("recipes.json", "materials.json")
    for grocery_item in shopping_cart.get_shopping_list():
        print(f"- {grocery_item.quantity:.2} {grocery_item.material.name}")


if __name__ == "__main__":
    main()
