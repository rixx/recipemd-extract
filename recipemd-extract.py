#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import codecs
import sys
import argparse
from argparse import RawTextHelpFormatter
from recipe import Recipe,Ingredient
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
		if(pluginFile.endswith('.py')):
			pluginName='.'+pluginFile[:-3]

			try:
				plugin=importlib.import_module(pluginName,'plugins')
				plugin.Ingredient=Ingredient
				plugin.Recipe=Recipe
				recipe=plugin.extract(url,soup)
				if isinstance(recipe,Recipe):
					return recipe
			except Exception as e:
				if debug:
					raise e
				print('In plugin "',pluginName,'": Error parsing recipe:',e)


def main():
	parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
	parser.add_argument('url', help='URL of the recipe')
	parser.add_argument('filename', help='the file to write to')
	parser.add_argument('--debug',action='store_true', help='enables debug mode')
	args = parser.parse_args()
	url = args.url
	filename = args.filename

	recipe=extract(url,args.debug)

	if(recipe):
		recipe.write(filename)
	else:
		print ('Could not extract recipe')


if __name__ == "__main__":
	main()
