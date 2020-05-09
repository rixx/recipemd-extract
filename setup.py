import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="recipemd-extract",
	version="1.1.0",
	author='AberDerBart',
	author_email='nonatz@web.de',
	description="Extracts recipes from websites and saves them in the RecipeMD format",
	long_description=long_description,
	long_description_content_type="text/markdown",
	packages=setuptools.find_packages(),
	python_requires='>=3.7,<4',
	install_requires=[
		'recipemd~=4.0.3',
		'beautifulsoup4~=4.7.1',
		'requests~=2.22.0',
		'html5lib==1.0.1',
		'scrape-schema-recipe==0.0.4',
		'recipe-scrapers==5.3.0',
	],
	entry_points={
		'console_scripts': [
			'recipemd-extract=recipemd_extract.main:main',
		],
	},
	classifiers=[
		"Development Status :: 4 - Beta",
		"Environment :: Console",
		"Intended Audience :: End Users/Desktop",
		"Programming Language :: Python :: 3",
		"Topic :: Utilities",
		"Topic :: Text Processing :: Markup",
		"Operating System :: OS Independent",
	],
	project_urls={
		'Source': 'https://github.com/AberDerBart/recipemd-extract',
	},
)
