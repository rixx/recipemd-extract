from recipe_scrapers import WebsiteNotImplementedError, scrape_html
from recipemd.data import Ingredient, Recipe, RecipeParser


def extract(url, _):
    try:
        scraper = scrape_html(html=None, org_url=url, online=True)
    except WebsiteNotImplementedError:
        return None

    try:
        description = f"![]({scraper.image()})"
    except NotImplementedError:
        description = ""

    recipe = Recipe(
        title=scraper.title(),
        description=description,
        yields=[RecipeParser.parse_amount(scraper.yields())],
        ingredients=[Ingredient(name=ingred) for ingred in scraper.ingredients()],
        instructions=scraper.instructions(),
    )

    return recipe
