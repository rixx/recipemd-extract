import requests
from bs4 import BeautifulSoup
from recipemd.data import RecipeParser,Recipe,Ingredient,IngredientGroup


def getJson(url,recipeId):
	# remove queries, fragments
	url=url.split('?')[0]
	url=url.split('#')[0]

	if(url.lower().startswith('http://') or url.lower().startswith('https://')):
		splitted=url.split('/')
		url = splitted[0] + '//' + splitted[2]
	
	r = requests.get(url + '/wp-json/wp/v2/wprm_recipe/' + recipeId)

	if(r.ok):
		return r.json()
	else:
		return None
	
def getText(html):
	return BeautifulSoup(html,'html5lib').text.strip()

def extract(url,soup):
	recipe_id_element = soup.find(attrs={'data-recipe-id':True,'class':'wprm-recipe-container'})

	if not recipe_id_element:
		return

	recipe_id = recipe_id_element.attrs['data-recipe-id']

	data=getJson(url,recipe_id)

	try:
		# title
		title = getText(data['recipe']['name'])
		# summary
		summary = getText(data['recipe']['summary'])
		# servings and tags
		servings = data['recipe']['servings']
		servings_unit = data['recipe']['servings_unit']
		
		tags = ['{} {}'.format(servings,servings_unit).strip()]

		for tagGroup in data['recipe']['tags'].values():
			for tag in tagGroup:
				tags.append(tag['name'])
		# ingredients
		ingredients=[]

		for ingredGroup in data['recipe']['ingredients']:
			group = IngredientGroup()
			if 'name' in ingredGroup:
				group.title = getText(ingredGroup['name'])
			for ingred in ingredGroup['ingredients']:
				amount, _ = RecipeParser.parse_amount(ingred['amount'])
				unit = ingred['unit'].strip()
				name = getText('{} {}'.format(ingred['name'],ingred['notes']))
				if unit == '':
					unit=None
				group.children.append(Ingredient(name,amount,unit))
			ingredients.append(group)
		# instructions
		instructions = ''

		for instrGroup in data['recipe']['instructions']:
			if 'name' in instrGroup:
				instructions = instructions + '## ' + getText(instrGroup['name']) + '\n'
			for index,instr in enumerate(instrGroup['instructions']):
				instructions = instructions + '{}. {}\n'.format(index + 1,getText(instr['text']))

		if 'notes' in data['recipe']:
			instructions = instructions + '\n## Recipe Notes\n\n' + getText(data['recipe']['notes'])

		return Recipe(title=title, ingredients=ingredients, instructions=instructions, description=summary, tags=tags)
	except Exception as e:
		print('failed to extract json:',e)
	# if the json extraction fails, try to extract data from website

	# title
	title = soup.find(attrs={'class': 'wprm-recipe-name'}).text.strip()
	# summary
	summary = soup.find('div',attrs={'class':'wprm-recipe-summary'}).text.strip()
	# servings and tags
	servings = soup.find('span',attrs={'class':'wprm-recipe-details wprm-recipe-servings'}).text.strip()
	servingsUnit = soup.find('span', attrs={'class':'wprm-recipe-details-unit wprm-recipe-servings-unit'}).text.strip()
	tags=['{} {}'.format(servings,servingsUnit)]

	courseTags=soup.find('span',attrs={'class':'wprm-recipe-course'})
	if courseTags:
		courseTags=courseTags.text.split(',')
	else:
		courseTags=[]
	cuisineTags=soup.find('span',attrs={'class':'wprm-recipe-cuisine'})
	if cuisineTags:
		cuisineTags=cuisineTags.text.split(',')
	else:
		cuisineTags=[]
	keywords = soup.find('span',attrs={'class':'wprm-recipe-keyword'})
	if keywords:
		keywords=keywords.text.split(',')
	else:
		keywords=[]
	for tag in courseTags + cuisineTags + keywords:
		tags.append(tag.strip())
	
	# ingredients
	ingreds=[]
	ingredGroups = soup.find_all('div', attrs={'class':'wprm-recipe-ingredient-group'})
	for ingredGroup in ingredGroups:
		group = IngredientGroup()
		groupName=ingredGroup.find('h4', attrs={'class':'wprm-recipe-group-name wprm-recipe-ingredient-group-name'})
		if(groupName):
			group.title = groupName.text.strip()
		groupIngreds=ingredGroup.find_all('li', attrs={'class':'wprm-recipe-ingredient'})
		for ingred in groupIngreds:
			amount = ingred.find('span',attrs={'class':'wprm-recipe-ingredient-amount'})
			if amount:
				amount, _=RecipeParser.parse_amount(amount.text)
			else:
				amount=None
			unit=ingred.find('span',attrs={'class':'wprm-recipe-ingredient-unit'})
			if unit:
				unit=unit.text.strip()
			else:
				unit=None
			name=ingred.find('span',attrs={'class':'wprm-recipe-ingredient-name'})
			if name:
				name=name.text.strip()
			else:
				name=''
			notes=ingred.find('span',attrs={'class':'wprm-recipe-ingredient-notes'})
			if notes:
				notes=notes.text.strip()
			else:
				notes=''
			group.children.append(Ingredient('{} {}'.format(name,notes).strip(), amount=amount, unit=unit))
		ingreds.append(group)

	# instructions
	instructions=''
	instructGroups=soup.find_all('div',attrs={'class':'wprm-recipe-instruction-group'})
	for ingredGroup in instructGroups:
		groupName=ingredGroup.find('h4',attrs={'class':'wprm-recipe-group-name wprm-recipe-instruction-group-name'})

		if groupName:
			instructions = instructions + '## ' + groupName.text.strip() + '\n'
		
		groupInstructs= ingredGroup.find_all('li', attrs={'class':'wprm-recipe-instruction'})
		for index,inst in enumerate(groupInstructs):
			instructions = instructions + str(index+1) + '. ' + inst.text.strip() +'\n'
	# notes
	notesContainer = soup.find('div',attrs={'class':'wprm-recipe-notes-container'})
	if notesContainer:
		notesTitle = notesContainer.find(attrs={'class':'wprm-recipe-header'}).text.strip()
		instructions = instructions + '\n## ' + notesTitle
		for p in notesContainer.find_all('p'):
			instructions= instructions + '\n\n' + p.text.strip()


	return Recipe(title=title, ingredients=ingreds, instructions=instructions, description=summary, tags=tags)
