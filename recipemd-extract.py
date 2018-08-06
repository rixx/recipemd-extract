#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import codecs
import sys
import argparse
from argparse import RawTextHelpFormatter
from recipe import Recipe,Ingredient

def yupitsvegan(soup):
	# title
	title = soup.find('h2', attrs={'class': 'wprm-recipe-name'}).text.strip()
	# TODO: error handling
	# summary
	summary = soup.find('div',attrs={'class':'wprm-recipe-summary'}).text.strip()
	# servings and tags
	servings = soup.find('span',attrs={'class':'wprm-recipe-details wprm-recipe-servings'}).text.strip()
	tags=['servings: {}'.format(servings)]
	# ingredients
	ingreds=[]
	ingredGroups = soup.find_all('div', attrs={'class':'wprm-recipe-ingredient-group'})
	for group in ingredGroups:
		groupName=group.find('h4', attrs={'class':'wprm-recipe-group-name wprm-recipe-ingredient-group-name'}).text.strip()
		ingreds.append('#### '+groupName)
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
		groupName=group.find('h4',attrs={'class':'wprm-recipe-group-name wprm-recipe-instruction-group-name'}).text.strip()
		instructions = instructions + '#### ' + groupName + '\n'
		
		groupInstructs= group.find_all('li', attrs={'class':'wprm-recipe-instruction'})
		for index,inst in enumerate(groupInstructs):
			instructions = instructions + str(index+1) + '. ' + inst.text.strip() +'\n'
	# notes
	notesContainer = soup.find('div',attrs={'class':'wprm-recipe-notes-container'})
	if notesContainer:
		notesTitle = notesContainer.find('h3').text.strip()
		instructions = instructions + '\n## ' + notesTitle
		for p in notesContainer.find_all('p'):
			instructions= instructions + '\n\n' + p.text.strip()


	return Recipe(title, ingreds, instructions, summary, tags)

def chefkoch(soup):
	# title
	title = soup.find('h1', attrs={'class': 'page-title'}).text
	if title == 'Fehler: Seite nicht gefunden' or title == 'Fehler: Rezept nicht gefunden':
		raise ValueError('No recipe found, check URL')
	# summary
	summary = soup.find('div', attrs={'class': 'summary'}).text
	# servings and tags
	servings= soup.find('input', attrs={'id':'divisor'}).attrs['value']
	tags=['{} Portion{}'.format(servings, 'en' if int(servings) > 1 else '')]

	tagcloud=soup.find('ul', attrs={'class':'tagcloud'})
	for tag in tagcloud.find_all('a'):
		tags.append(tag.text)
	# ingredients
	ingreds = []
	table = soup.find('table', attrs={'class': 'incredients'})
	rows = table.find_all('tr')

	ingreds=[]
	for row in rows:
		cols = row.find_all('td')
		cols = [s.text.strip() for s in cols]
		ingreds.append(Ingredient(cols[1],cols[0]))
	# instructions
	instruct = soup.find('div', attrs={'id': 'rezept-zubereitung'}).text  # only get text
	instruct = instruct.strip()  # remove leadin and ending whitespace
	# write to file
	return Recipe(title, ingreds, instruct, summary, tags)

def main():
	parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
	parser.add_argument('url', help='URL of the recipe')
	parser.add_argument('filename', help='the file to write to')
	args = parser.parse_args()
	url = args.url
	filename = args.filename
	try:
		page = requests.get(url)
	except Exception:
		print('No valid URL')
		sys.exit(1)
	soup = BeautifulSoup(page.text, "html5lib")

	if 'www.chefkoch.de/' in url:
		chefkoch(soup).write(filename)
	elif 'yupitsvegan.com' in url:
		yupitsvegan(soup).write(filename)
	else:
		print ('Website not supported')


if __name__ == "__main__":
	main()
