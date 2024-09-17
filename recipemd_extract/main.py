#!/usr/bin/env python

import argparse
import sys
from argparse import RawTextHelpFormatter
from contextlib import suppress

from recipemd.data import Recipe, RecipeSerializer

from recipemd_extract.parsers.recipe_schema import extract_schema
from recipemd_extract.parsers.recipe_scrapers import extract_recipe_scrapers
from recipemd_extract.parsers.wprm import extract_wordpress


def extract(url):
    # First, try to download the recipe with recipe_scrapers.
    # Failing that, we fall back to JSON-LD parsing or checking if the page
    # is a WordPress site with WP Recipe Maker.

    parsers = [
        extract_recipe_scrapers,
        extract_schema,
        extract_wordpress,
    ]

    recipe = None

    for parser in parsers:
        with suppress(Exception):
            recipe = parser(url)
        if recipe:
            return recipe


def write_recipe(recipe, filename=None):
    if not filename:
        filename = "_".join(recipe.title.lower().split())
        filename = "".join(c for c in filename if (c.isalnum() or c in "._-")) + ".md"
    with open(filename, "w") as fp:
        fp.write(RecipeSerializer().serialize(recipe))
    return filename


def main():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument("url", help="URL of the recipe")
    parser.add_argument(
        "filename",
        help="The file to write to – will be derived from the recipe title if not given",
        nargs="?",
        default=None,
    )
    args = parser.parse_args()

    recipe = extract(args.url)

    if isinstance(recipe, Recipe):
        result = write_recipe(recipe, args.filename)
        print("Recipe written to " + result)
    else:
        print(recipe, file=sys.stderr)
        print("Could not extract recipe")
        sys.exit(1)


if __name__ == "__main__":
    main()
