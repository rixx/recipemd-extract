#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import codecs
import sys
import argparse
from argparse import RawTextHelpFormatter
from recipemd.data import RecipeSerializer,Recipe,Ingredient
import importlib
import os


def extract(url, debug=False):
	try:
		page = requests.get(url)
	except Exception:
		print('No valid URL')
		sys.exit(1)
	soup = BeautifulSoup(page.text, "html5lib")

	pluginFilelist=os.listdir(os.path.dirname(os.path.realpath(__file__))+'/plugins')

	for pluginFile in pluginFilelist:
		if(pluginFile.endswith('.py') and pluginFile != "__init__.py"):
			pluginName='.'+pluginFile[:-3]

			try:
				plugin=importlib.import_module(pluginName,'recipemd_extract.plugins')
				recipe=plugin.extract(url,soup)
				if isinstance(recipe,Recipe):
					return recipe
			except Exception as e:
				if debug:
					raise e
				print('In plugin "',pluginName,'": Error parsing recipe:',e)

def writeRecipe(recipe, filename=None):
	if not filename:
		joinedTitle = '_'.join(recipe.title.lower().split())
		filename = ''.join(c for c in joinedTitle if (c.isalnum() or c in '._')) + '.md'
	with codecs.open(filename, 'w', encoding="utf-8") as f:
		f.write(RecipeSerializer().serialize(recipe))


def main():
	parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
	parser.add_argument('url', help='URL of the recipe')
	parser.add_argument('filename', help='the file to write to',nargs='?',default=None)
	parser.add_argument('--debug',action='store_true', help='enables debug mode')
	args = parser.parse_args()
	url = args.url
	filename = args.filename

	recipe=extract(url,args.debug)

	if(recipe):
		writeRecipe(recipe, filename)
	else:
		print ('Could not extract recipe')


if __name__ == "__main__":
	main()
