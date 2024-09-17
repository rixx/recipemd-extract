from recipe_scrapers import WebsiteNotImplementedError, scrape_html
from recipemd.data import Ingredient, Recipe, RecipeParser


def extract_recipe_scrapers(url):
    try:
        scraper = scrape_html(html=None, org_url=url, online=True)
    except WebsiteNotImplementedError:
        return

    try:
        description = f"![]({scraper.image()})"
    except NotImplementedError:
        description = ""

    return Recipe(
        title=scraper.title(),
        description=description,
        yields=[RecipeParser.parse_amount(scraper.yields())],
        ingredients=[Ingredient(name=ingred) for ingred in scraper.ingredients()],
        instructions=scraper.instructions(),
    )
