def extract(url,soup):
	recipe_id_element = soup.find(attrs={'data-recipe-id':True,'class':'wprm-recipe-container'})

	if not recipe_id_element:
		return

	recipe_id = recipe_id_element.attrs['data-recipe-id']

	# TODO: extract the json

	# title
	title = soup.find(attrs={'class': 'wprm-recipe-name'}).text.strip()
	# TODO: error handling
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
	for group in ingredGroups:
		groupName=group.find('h4', attrs={'class':'wprm-recipe-group-name wprm-recipe-ingredient-group-name'})
		if(groupName):
			ingreds.append('#### '+groupName.text.strip())
		groupIngreds=group.find_all('li', attrs={'class':'wprm-recipe-ingredient'})
		for ingred in groupIngreds:
			amount=ingred.find('span',attrs={'class':'wprm-recipe-ingredient-amount'})
			if amount:
				amount=amount.text.strip()
			else:
				amount=''
			unit=ingred.find('span',attrs={'class':'wprm-recipe-ingredient-unit'})
			if unit:
				unit=unit.text.strip()
			else:
				unit=''
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
			ingreds.append(Ingredient('{} {}'.format(name,notes).strip(), '{} {}'.format(amount, unit).strip()))

	# instructions
	instructions=''
	instructGroups=soup.find_all('div',attrs={'class':'wprm-recipe-instruction-group'})
	for group in instructGroups:
		groupName=group.find('h4',attrs={'class':'wprm-recipe-group-name wprm-recipe-instruction-group-name'})

		if groupName:
			instructions = instructions + '#### ' + groupName.text.strip() + '\n'
		
		groupInstructs= group.find_all('li', attrs={'class':'wprm-recipe-instruction'})
		for index,inst in enumerate(groupInstructs):
			instructions = instructions + str(index+1) + '. ' + inst.text.strip() +'\n'
	# notes
	notesContainer = soup.find('div',attrs={'class':'wprm-recipe-notes-container'})
	if notesContainer:
		notesTitle = notesContainer.find(attrs={'class':'wprm-recipe-header'}).text.strip()
		instructions = instructions + '\n## ' + notesTitle
		for p in notesContainer.find_all('p'):
			instructions= instructions + '\n\n' + p.text.strip()


	return Recipe(title, ingreds, instructions, summary, tags)
