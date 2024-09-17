import urllib.parse
from contextlib import suppress
from dataclasses import replace

import requests
from bs4 import BeautifulSoup
from recipemd.data import Ingredient, IngredientGroup, Recipe, RecipeParser


def getJson(url, recipe_id):
    domain = urllib.parse.urlparse(url).netloc
    json_url = f"https://{domain}/wp-json/wp/v2/wprm_recipe/{recipe_id}"
    response = requests.get(json_url)
    response.raise_for_status()
    return response.json()


def get_text(html):
    return BeautifulSoup(html, "html5lib").text.strip()


def extract_wordpress(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, "html5lib")

    parsers = [
        extract_wordpress_json,
        extract_wordpress_html,
    ]

    recipe = None
    for parser in parsers:
        with suppress(Exception):
            recipe = parser(soup, url)
        if recipe:
            return recipe


def extract_wordpress_json(soup, url):
    recipe_id_element = soup.find(
        attrs={"data-recipe-id": True, "class": "wprm-recipe-container"}
    )
    if not recipe_id_element:
        return

    recipe_id = recipe_id_element.attrs["data-recipe-id"]
    data = (url, recipe_id)

    title = get_text(data["recipe"]["name"])
    summary = get_text(data["recipe"]["summary"])
    servingsAmount = RecipeParser.parse_amount(data["recipe"]["servings"])
    servingsUnit = data["recipe"]["servings_unit"]
    if servingsUnit != "":
        servingsAmount = replace(servingsAmount, unit=servingsUnit)
    yields = [servingsAmount]

    tags = []
    for tagGroup in data["recipe"]["tags"].values():
        for tag in tagGroup:
            tags.append(tag["name"])

    ingredients = []
    for ingredGroup in data["recipe"]["ingredients"]:
        children = []
        if "name" in ingredGroup:
            title = get_text(ingredGroup["name"])
        else:
            title = None
        for ingred in ingredGroup["ingredients"]:
            amount = RecipeParser.parse_amount(ingred["amount"])
            unit = ingred["unit"].strip()
            if unit != "":
                amount = replace(amount, unit=unit)
            name = get_text("{} {}".format(ingred["name"], ingred["notes"]))
            children.append(Ingredient(name, amount))
        group = IngredientGroup(title=title, ingredients=children)
        ingredients.append(group)

    instructions = ""
    for instrGroup in data["recipe"]["instructions"]:
        if "name" in instrGroup:
            instructions = instructions + "## " + get_text(instrGroup["name"]) + "\n"
        for index, instr in enumerate(instrGroup["instructions"]):
            instructions = instructions + "{}. {}\n".format(
                index + 1, get_text(instr["text"])
            )

    if "notes" in data["recipe"]:
        instructions = (
            instructions + "\n## Recipe Notes\n\n" + get_text(data["recipe"]["notes"])
        )

    instructions += f"\n\n[Original Recipe]({url})"

    return Recipe(
        title=title,
        ingredients=ingredients,
        instructions=instructions,
        description=summary,
        tags=tags,
        yields=yields,
    )


def extract_wordpress_html(soup, url):
    title = soup.find(attrs={"class": "wprm-recipe-name"}).text.strip()
    summary = soup.find("div", attrs={"class": "wprm-recipe-summary"}).text.strip()

    yields = []
    servings = soup.find(
        "span", attrs={"class": "wprm-recipe-details wprm-recipe-servings"}
    )
    if servings:
        servingsAmount = RecipeParser.parse_amount(servings.text.strip())
        servingsUnit = soup.find(
            "span",
            attrs={"class": "wprm-recipe-details-unit wprm-recipe-servings-unit"},
        ).text.strip()
        if servingsUnit != "":
            servingsAmount = replace(servingsAmount, unit=servingsUnit)
        yields.append(servingsAmount)

    tags = []
    courseTags = soup.find("span", attrs={"class": "wprm-recipe-course"})
    if courseTags:
        courseTags = courseTags.text.split(",")
    else:
        courseTags = []
    cuisineTags = soup.find("span", attrs={"class": "wprm-recipe-cuisine"})
    if cuisineTags:
        cuisineTags = cuisineTags.text.split(",")
    else:
        cuisineTags = []
    keywords = soup.find("span", attrs={"class": "wprm-recipe-keyword"})
    if keywords:
        keywords = keywords.text.split(",")
    else:
        keywords = []
    for tag in courseTags + cuisineTags + keywords:
        tags.append(tag.strip())
    tags = list(set(tags))

    ingreds = []
    ingredGroups = soup.find_all("div", attrs={"class": "wprm-recipe-ingredient-group"})
    for ingredGroup in ingredGroups:
        groupName = ingredGroup.find(
            "h4",
            attrs={"class": "wprm-recipe-group-name wprm-recipe-ingredient-group-name"},
        )
        if groupName:
            title = groupName.text.strip()
        else:
            title = None
        groupIngreds = ingredGroup.find_all(
            "li", attrs={"class": "wprm-recipe-ingredient"}
        )
        children = []
        for ingred in groupIngreds:
            amount = ingred.find(
                "span", attrs={"class": "wprm-recipe-ingredient-amount"}
            )
            if amount:
                amount = RecipeParser.parse_amount(amount.text)
            else:
                amount = None
            unit = ingred.find("span", attrs={"class": "wprm-recipe-ingredient-unit"})
            if unit:
                amount = replace(amount, unit=unit.text)
            name = ingred.find("span", attrs={"class": "wprm-recipe-ingredient-name"})
            if name:
                name = name.text.strip()
            else:
                name = ""
            notes = ingred.find("span", attrs={"class": "wprm-recipe-ingredient-notes"})
            if notes:
                notes = notes.text.strip()
            else:
                notes = ""
            children.append(
                Ingredient("{} {}".format(name, notes).strip(), amount=amount)
            )
        group = IngredientGroup(title=title, ingredients=children)
        ingreds.append(group)

    instructions = ""
    instructGroups = soup.find_all(
        "div", attrs={"class": "wprm-recipe-instruction-group"}
    )
    for ingredGroup in instructGroups:
        groupName = ingredGroup.find(
            "h4",
            attrs={
                "class": "wprm-recipe-group-name wprm-recipe-instruction-group-name"
            },
        )

        if groupName:
            instructions = instructions + "## " + groupName.text.strip() + "\n"

        groupInstructs = ingredGroup.find_all(
            "li", attrs={"class": "wprm-recipe-instruction"}
        )
        for index, inst in enumerate(groupInstructs):
            instructions = (
                instructions + str(index + 1) + ". " + inst.text.strip() + "\n"
            )

    notesContainer = soup.find("div", attrs={"class": "wprm-recipe-notes-container"})
    if notesContainer:
        notesTitle = notesContainer.find(
            attrs={"class": "wprm-recipe-header"}
        ).text.strip()
        instructions = instructions + "\n## " + notesTitle
        for p in notesContainer.find_all("p"):
            instructions = instructions + "\n\n" + p.text.strip()

    instructions += f"\n\n[Original Recipe]({url})"

    return Recipe(
        title=title,
        ingredients=ingreds,
        instructions=instructions,
        description=summary,
        tags=tags,
        yields=yields,
    )
