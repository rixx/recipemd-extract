## recipemd-extract

recipemd-extract extracts recipes from websites and saves them in the [recipemd](https://github.com/tstehr/recipemd/blob/master/specification.md) format. It is based on [recipemd-cli](https://github.com/dnlvgl/recipemd-cli).

## supported websites

1. chefkoch.de
2. seriouseats.com
3. Any Wordpress blog using [WP Recipe Manager](https://en-ca.wordpress.org/plugins/wp-recipe-manager/)
4. Any page supported by [recipe-scrapers](https://github.com/hhursev/recipe-scrapers)

## requirements

- [recipemd](https://github.com/tstehr/recipemd)
- [beautifulsoup4](http://www.crummy.com/software/BeautifulSoup/)
- [requests](http://docs.python-requests.org/en/latest/user/install/)
- [html5lib](https://github.com/html5lib/html5lib-python)
- [scrape-schema-recipe](https://github.com/micahcochran/scrape-schema-recipe)
- [recipe-scrapers](https://github.com/hhursev/recipe-scrapers)

## usage

`python recipemd.py 'url-of-recipe'`
