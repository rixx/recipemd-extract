#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import codecs
import sys
import argparse
from argparse import RawTextHelpFormatter
from recipe import Recipe,Ingredient


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
	else:
		print ('Website not supported')


if __name__ == "__main__":
	main()
