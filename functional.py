from functools import partial, reduce
from itertools import chain
from typing import List, Dict, Iterable

from astropy import units as u

from data_models import MaterialData, IngredientData, RecipeData
from pydantic_finagling import (
    mass_type,
    volume_type,
    load_list,
)

u.imperial.enable()


def regularize_ingredient(
    ingredient: IngredientData, known_materials: Dict[str, MaterialData]
) -> IngredientData:
    """Adjust the quantity of an ingredient to match the preferred units of known materials."""
    # Get the matching material
    material = known_materials.get(ingredient.item)

    # If a matching material was found, check to see if a conversion of physical types is
    # required (for example, from mass to volume). In the end, make to use the preferred
    # units.
    if material:
        if ingredient.quantity.unit.physical_type == material.unit.physical_type:
            quantity = ingredient.quantity
        elif ingredient.quantity.unit.physical_type == mass_type:
            quantity = ingredient.quantity / material.mass_per_unit
        elif ingredient.quantity.unit.physical_type == volume_type:
            quantity = ingredient.quantity / material.volume_per_unit
        else:
            raise ValueError(
                f"Cannot regularize {ingredient.item} with {ingredient.quantity}. Preferred unit is {material.unit}"
            )
        return IngredientData(quantity=quantity.to(material.unit), item=ingredient.item)

    # There was no match, so nothing to do. These items will be much less likely to merge.
    return ingredient


def regularize_recipe(recipe: RecipeData, known_materials: Dict[str, MaterialData]) -> RecipeData:
    """Adjust the ingredients for the given recipe."""
    return RecipeData(
        name=recipe.name,
        source=recipe.source,
        instructions=recipe.instructions,
        ingredients=[
            regularize_ingredient(ingredient, known_materials)
            for ingredient in recipe.ingredients
        ],
    )


def add_recipe_to_ingredients(
    ingredients: Iterable[IngredientData], recipe: RecipeData
) -> Iterable[IngredientData]:
    """Add the ingredients in a recipe to the overall list of ingredients."""
    return reduce(
        # Compare each ingredient with the end of the list. If it is the same item, merge them.
        # Otherwise, just add them to the list separately.
        lambda merged_ingredients, ingredient: merged_ingredients[:-1]
        + [
            IngredientData(
                item=ingredient.item,
                quantity=ingredient.quantity + merged_ingredients[-1].quantity,
            )
        ]
        if merged_ingredients and ingredient.item == merged_ingredients[-1].item
        else merged_ingredients + [ingredient],

        # Append the recipe's ingredients to the overall list of ingredients, then
        # sort the result by item name, so that same-named items will be next to each
        # other. We are assuming that only one of each ingredient is listed in the recipe
        # or in the overall list of ingredients (generally a reasonable assumption, but future
        # improvements could handle the exception to that rule).
        sorted(
            chain(ingredients, recipe.ingredients),
            key=lambda ingredient: ingredient.item,
        ),

        # Initialize with an empty list.
        [],
    )


def create_grocery_list(
    recipes: Iterable[RecipeData], material_definitions: List[MaterialData]
) -> Iterable[IngredientData]:
    """Generate a grocery list for the given list of recipes."""
    # Turn the list of materials into a lookup table for efficient use.
    material_lookup = {material.name: material for material in material_definitions}

    # Merge each recipe into the list of ingredients.
    return reduce(
        # Apply the function defined above.
        add_recipe_to_ingredients,

        # Apply the regularization to all the recipes before they go through.
        map(partial(regularize_recipe, known_materials=material_lookup), recipes),

        # Initialize with an empty iterator.
        iter(()),
    )


def main():
    # Load a list of known materials from JSON
    material_definitions = load_list("materials.json", MaterialData.parse_obj)

    # Load the recipes from JSON
    recipes = load_list("recipes.json", RecipeData.parse_obj)

    # Create and print a grocery list for the given recipes.
    for grocery_item in create_grocery_list(recipes, material_definitions):
        print(f"- {grocery_item.quantity:.2} {grocery_item.item}")


if __name__ == "__main__":
    main()
