from functools import partial, reduce
from itertools import chain
from typing import List, Dict, Iterable

from astropy import units as u

from data_models import MaterialData, IngredientData, RecipeData, load_list


def regularize_ingredient(
        ingredient: IngredientData,
        known_materials: Dict[str, MaterialData]
) -> IngredientData:
    material = known_materials.get(ingredient.item)

    if material:
        if ingredient.quantity.unit.physical_type == material.unit.physical_type:
            quantity = ingredient.quantity
        elif ingredient.quantity.unit.physical_type == u.get_physical_type("mass"):
            quantity = ingredient.quantity / material.mass_per_unit
        elif ingredient.quantity.unit.physical_type == u.get_physical_type("volume"):
            quantity = ingredient.quantity / material.volume_per_unit
        else:
            raise ValueError(
                f"Cannot regularize {ingredient.item} with {ingredient.quantity}. Preferred unit is {material.unit}"
            )
        return IngredientData(quantity=quantity.to(material.unit), item=ingredient.item)

    return ingredient


def regularize_recipe(
        recipe: RecipeData,
        known_materials: Dict[str, MaterialData]
) -> RecipeData:
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
        ingredients: Iterable[IngredientData],
        recipe: RecipeData
) -> Iterable[IngredientData]:
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
        # other.
        sorted(
            chain(ingredients, recipe.ingredients),
            key=lambda ingredient: ingredient.item,
        ),

        # Initialize with an empty list.
        [],
    )


def create_grocery_list(
        recipes: Iterable[RecipeData],
        material_definitions: List[MaterialData]
) -> Iterable[IngredientData]:
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
    material_definitions = load_list("materials.json", MaterialData.parse_obj)
    recipes = load_list("recipes.json", RecipeData.parse_obj)
    for grocery_item in create_grocery_list(recipes, material_definitions):
        print(f"- {grocery_item.quantity:.2} {grocery_item.item}")


if __name__ == "__main__":
    main()
