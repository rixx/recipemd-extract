from recipe_scrapers import scrape_me, WebsiteNotImplementedError
from recipemd.data import Recipe, RecipeParser, Ingredient


def extract(url, _):
	try:
		scraper = scrape_me(url)
	except WebsiteNotImplementedError:
		return None

	try:
		description = f'<img src="{scraper.image()}" />'
	except NotImplementedError:
		description = ''

	recipe = Recipe(
		title=scraper.title(),
		description=description,
		yields=[RecipeParser.parse_amount(scraper.yields())],
		ingredients=[Ingredient(name=ingred) for ingred in scraper.ingredients()],
		instructions=scraper.instructions(),
	)

	return recipe
