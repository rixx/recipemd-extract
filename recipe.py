import codecs

class Recipe:
	def __init__(self, title, ingredients, instructions, summary='', tags=[]):
		self.title=title
		self.ingr=ingredients
		self.instr=instructions
		self.summary=summary
		self.tags=tags
	def write(self, filename=None):
		if not filename:
			joinedTitle='_'.join(self.title.lower().split())
			filename = ''.join(c for c in joinedTitle if (c.isalnum() or c in '._')) + '.md'
		with codecs.open(filename, 'w', encoding="utf-8") as f:
			f.write('# ' + self.title + '\n\n')
			if(self.summary != ''):
				f.write('{}\n\n'.format(self.summary))
			if(self.tags != []):
				f.write('*{}*\n\n'.format(', '.join(self.tags)))
			f.write('---\n\n')

			for ingredient in self.ingr:
				f.write(str(ingredient)+'\n')

			f.write('\n---\n\n')
			f.write(self.instr)
			print('File written as: "{}"'.format(filename))

class Ingredient:
	def __init__(self, name, amount=None):
		self.name=name
		self.amount=amount
	def __str__(self):
		if self.amount:
			return '- *{}* {}'.format(self.amount,self.name)
		else:
			return '- {}'.format(self.name)
