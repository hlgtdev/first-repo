import sys

import yaml
import time
import re

from pathlib import Path
#
# TODO:
# =====
#
#	- Gérer la notion de macro:
#		Format: @inline nom_macro(param1, ..., paramN)
#		Exemple:
#			- 1-lined:	@inline getEntry(placeHolder, entry): placeHolder[entry]
#			- N-lined:	@inline bloc_d_operations()
#							operation1()
#							operation2()
#							operationN()
#		=> Alternative à la définition d'une méthode encapsulant du code (@def)
#		=> Le code caché dans la macro est directement produit
#
#	- Catégorie d'objet:
#		Format: catégorie/sous-catégorie/sous-sous-catégorie...
#		Exemple:
#			- Entrée/Source
#		=> pour lisibilité dans l'afficheur d'objets
#
#	- Contexte d'objet:
#		Format: contexte/sous-contexte/sous-sous-contexte...
#		Exemples:
#			- Feature: saisir une note
#			- Feature: saisir une note/à la souris
#			- Feature: saisir une note/au clavier
#		=> pour construire un diagramme d'objet par niveau de contexte
#		=> pour avoir des diagrammes de séquence spécifiques au niveau "feuille"
#
#	- UML: construire le diagramme de classe
#		- soit avec héritage UML avec relation
#			=> à la norme UML
#		- soit avec héritage UML avec stéréotype
#			=> non à la norme UML (facilité de lecture du diagramme)
#
#	- UML: construire le diagramme de navigation
#		- à partir des évènements menant à un AllerA(...) / retourner()
#
#	- Construire des documents:
#		- pour les différents contextes (feature, ...)
#		- mettant en relation les diagrammes UML
#		- détaillant les diagrammes UML
#
class Example():

	def isImported(pyFilename):

		return Path(pyFilename).stem in sys.modules
	#___________________________________________________________________________
	#
	def __init__(self):

		self.rootPackage = 'application'
		self.isClassPrefixUsed = True
		self.repository = {}
	#___________________________________________________________________________
	#
	def setRootPackage(self, rootPackage):

		self.rootPackage = rootPackage
	#___________________________________________________________________________
	#
	def useClassPrefix(self, bool):

		self.isClassPrefixUsed = bool
	#___________________________________________________________________________
	#
	def imports(self):
		pass
	#___________________________________________________________________________
	#
	def define(self):
		pass
	#___________________________________________________________________________
	#
	def process(self):
		pass
	#___________________________________________________________________________
	#
	def run(self):

		self.define()
		self.process()
	#___________________________________________________________________________
	#
	def importExamples(self, examples):
		pass
	#___________________________________________________________________________
	#
	def importProcessors(self, examples):
		pass
	#___________________________________________________________________________
	#
	def newRef(self):

		return 'REF_%s' % int(time.time() * 1E+7)
	#___________________________________________________________________________
	#
	def importValues(self, examples):
		pass
	#___________________________________________________________________________
	#
	def showErrorContext(self, ref):

		maxLines = 256
		separator = '#' * 140
		context = self.showValue(ref, silent=True)
		nbLinesContext = len(context)
		limitedContext = '### %s' % '\n### '.join(context[ 0 : min(maxLines, nbLinesContext) ])

		print(separator)
		print("### [CONTEXTE DE L'ERREUR]")
		print(separator)
		print(limitedContext)

		if maxLines < nbLinesContext:
			print('### [...]')
			print('### [%d LIGNES AFFICHEES SUR %d]' % (maxLines, nbLinesContext))
		print(separator)
	#___________________________________________________________________________
	#
	def debug(self, value, info=''):

		ref = ('[DEBUG:%s] %s' % (self.newRef(), info)).strip()

		self.setValue(ref=ref, value=value)
	#___________________________________________________________________________
	#
	def loadSourceCode(self, filename):

		with open(filename, 'r') as file:
			lines = file.read().splitlines()

		classId = None
		methodId = None
		imports = []
		body = []

		for line in lines:
			if re.search(r'import\s+.+|from\s+.+\s+import.+', line) is not None:
				imports.append(line.strip())
			else:
				m = re.search(r'@class\s+(.+)\s*', line)

				if m is not None:
					classId = m.group(1)

					ref = 'input.source.Code::%s' % classId

					self.setValue(ref, './@class', 'input.source.Code')
					self.setValue(ref, './id', classId)
				else:
					m = re.search(r'@def\s+(.+)\s*', line)

					if m is not None:
						if classId is not None and methodId is not None:
							for i in range(-1, 1):
								while body[i].strip() == '':
									body.pop(i)

							self.setValue(ref, './methods/%s/id' % methodId, methodId)
							self.setValue(ref, './methods/%s/imports/lines' % methodId, imports)
							self.setValue(ref, './methods/%s/body/lines' % methodId, body)

						methodId = m.group(1)

						if not methodId.endswith(')'):
							raise ValueError('\n###\n### [SYNTAX ERROR] La méthode doit se terminer par ")":\n### %s\n###' % methodId)

						imports = []
						body = []
					else:
						body.append(line)

		if classId is not None and methodId is not None:
			for i in range(-1, 1):
				while body[i].strip() == '':
					body.pop(i)

			self.setValue(ref, './methods/%s/id' % methodId, methodId)
			self.setValue(ref, './methods/%s/imports/lines' % methodId, imports)
			self.setValue(ref, './methods/%s/body/lines' % methodId, body)
	#___________________________________________________________________________
	#
	def setObject(self, objectAsMap, idName='id', className='@class'):

		classValue = ''

		if self.isClassPrefixUsed is True:
			classValue = ('%s::' % objectAsMap[className]) if className in objectAsMap else ''

		idValue	= objectAsMap[idName] if idName in objectAsMap else ''
		ref		= '%s%s' % (classValue, idValue)
		ref		= '%s%s' % (ref, self.newRef()) if ref.endswith('::') else ref
		ref		= None if ref.strip() == '' else ref

		newRef = self.setValue(ref=ref, value=objectAsMap)
		modelObjects = self.findAll(ref=newRef, select='.+/', where='./.+/@class ')

		for accessor, modelObject in modelObjects.items():
			classe = self.getValue(modelObject, './@class', default=None)
			id = self.getValue(modelObject, './id', default=None)

			if classe is not None and id is not None:
				ref = '%s::%s' % (classe, id)

				if self.getValue(ref, default=None) == None:
					self.setObject(modelObject)

		return newRef
	#___________________________________________________________________________
	#
	def getYamlObject(self, yamlSource):

		yamlSource = yamlSource.replace('\t', 4 * ' '
			).replace('-    ', '-   '
			)
		try:
			value = yaml.safe_load(yamlSource)
		except:
			separator = '#' * 140
			lines = yamlSource.split('\n')

			print(separator)
			print('### SOURCE Yaml INCORRECT')
			print(separator)

			for n, line in enumerate(lines, 1):
				print('### %d: %s' % (n, line))

			print(separator)
			raise

		return value
	#___________________________________________________________________________
	#
	def setYamlObject(self, yamlSource, idName='id', className='@class', **args):

		if len(args) > 0:
			yamlSource = yamlSource.format(**args)

		value = self.getYamlObject(yamlSource)

		if isinstance(value, list) or isinstance(value, dict):
			return self.setObject(value)
		else:
			self.setValue(value=value)
	#___________________________________________________________________________
	#
	def getValue(self, ref=None, accessor='.', default=Exception, setDefault=False):

		currentPlaceHolder = ref if isinstance(ref, dict) or isinstance(ref, list) else self.repository
		basePlaceHolder = currentPlaceHolder
		currentValue = None
		hasToRaiseException = default == Exception

		if accessor == '.':
			if isinstance(ref, str) and ref not in currentPlaceHolder:
				if hasToRaiseException is True:
					self.showErrorContext(currentPlaceHolder)
					raise ValueError("### REFERENCE [%s] NON TROUVEE DANS LE CONTEXTE" % ref)

				if setDefault is True:
					self.setValue(ref=ref, accessor=accessor, value=default)
				return default

			if ref is None:
				return currentPlaceHolder
			elif isinstance(ref, dict):
				return ref
			elif isinstance(ref, list):
				return ref
			else:
				return currentPlaceHolder[ref]

		refMessage = ' POUR LA REFERENCE [%s]' % ref if isinstance(ref, str) else ''
		keys = [ item for item in accessor.split('/') if item.strip() != '' ]

		if ref is not None and isinstance(ref, str):
			keys.insert(0, ref)

		for currentKey in keys:
			if currentKey == '.':
				continue

			if currentKey == '?' and len(currentPlaceHolder) == 1:
				# Accès anonyme au seul élément d'une collection
				if isinstance(currentPlaceHolder, dict) is True:
					currentPlaceHolder = list(currentPlaceHolder.values())[0]
				elif isinstance(currentPlaceHolder, list) is True:
					currentPlaceHolder = currentPlaceHolder[0]
				continue

			if currentPlaceHolder is None:
				if hasToRaiseException is True:
					self.showErrorContext(currentPlaceHolder)
					raise ValueError("### ELEMENT [%s] DE L'ACCESSOR [%s] NON TROUVE%s DANS LE CONTEXTE" % (
						currentKey, accessor, refMessage))

				if setDefault is True:
					self.setValue(ref=ref, accessor=accessor, value=default)
				return default
			elif isinstance(currentPlaceHolder, list):
				if currentKey.isdigit():
					currentKey = int(currentKey)
				else:
					self.showErrorContext(currentPlaceHolder)
					raise ValueError("### INDICE [%s] DE L'ACCESSOR [%s] INCORRECT%s DANS LE CONTEXTE" % (
						currentKey, accessor, refMessage))

				if currentKey >= len(currentPlaceHolder):
					if hasToRaiseException is True:
						self.showErrorContext(currentPlaceHolder)
						raise ValueError("### INDICE [%s] DE L'ACCESSOR [%s] NON TROUVE%s DANS LE CONTEXTE" % (
							currentKey, accessor, refMessage))

					if setDefault is True:
						self.setValue(ref=ref, accessor=accessor, value=default)
					return default
			elif isinstance(currentPlaceHolder, dict):
				if currentKey not in currentPlaceHolder:
					if hasToRaiseException is True:
						self.showErrorContext(currentPlaceHolder)
						raise ValueError("### CLE [%s] DE L'ACCESSOR [%s] NON TROUVEE%s DANS LE CONTEXTE" % (
							currentKey, accessor, refMessage))

					if setDefault is True:
						self.setValue(ref=ref, accessor=accessor, value=default)
					return default

			currentValue = currentPlaceHolder[currentKey]
			currentPlaceHolder = currentValue if isinstance(currentValue, dict) or isinstance(currentValue, list) else None

		return currentValue
	#___________________________________________________________________________
	#
	def setValue(self, ref=None, accessor='.', value=None):

		currentPlaceHolder = ref if isinstance(ref, dict) or isinstance(ref, list) else self.repository

		if accessor == '.':
			if not isinstance(ref, str):
				ref = self.newRef()
			currentPlaceHolder[ref] = value
			return ref if currentPlaceHolder == self.repository else None

		keys = [ item for item in accessor.split('/') if item.strip() != '' ]

		if ref is not None and isinstance(ref, str):
			keys.insert(0, ref)

		nbKeys = len(keys)

		for i, currentKey in enumerate(keys, 1):
			if currentKey == '.':
				continue

			if isinstance(currentPlaceHolder, list):
				currentKey = int(currentKey)
				currentKeyExists = currentKey < len(currentPlaceHolder)
			else:
				currentKeyExists = currentKey in currentPlaceHolder

			nextKey = keys[i] if i < nbKeys else None

			if nextKey is None:
				if isinstance(currentPlaceHolder, list):
					nb = len(currentPlaceHolder)

					if currentKey >= nb:
						nbToAdd = currentKey - nb + 1
						currentPlaceHolder.extend([ None ] * nbToAdd)

				currentPlaceHolder[currentKey] = value
				return

			nextPlaceHolder = None

			if nextKey.isdigit():
				rank = int(nextKey)
				nextPlaceHolder = [ None ] * (rank + 1)
			else:
				nextPlaceHolder = {}

			if currentKeyExists is True and isinstance(currentPlaceHolder[currentKey], type(nextPlaceHolder)):
				currentValue = currentPlaceHolder[currentKey]
			else:
				currentValue = nextPlaceHolder

			if isinstance(currentPlaceHolder, list):
				nb = len(currentPlaceHolder)

				if currentKey >= nb:
					nbToAdd = currentKey - nb + 1
					currentPlaceHolder.extend([ None ] * nbToAdd)

			currentPlaceHolder[currentKey] = currentValue
			currentPlaceHolder = currentValue
	#___________________________________________________________________________
	#
	def noRegExp(self, s):

		return s.replace('(', '\('
			).replace(')', '\)'
			).replace('[', '\['
			).replace(']', '\]'
			).replace('{', '\{'
			).replace('}', '\}'
			).replace('|', '\|'
			).replace('^', '\^'
			).replace('$', '\$'
			).replace('*', '\*'
			).replace('+', '\+'
			).replace('?', '\?'
			).replace('.', '\.'
			)
	#___________________________________________________________________________
	#
	def findAll(self, ref=None, select=None, where=None, sort=False):

		reSelect = '(.*?) ' if select is None else '(%s)' % select
		reWhere = '.*' if where is None else where

		lines = self.showValue(ref=ref, showEmpty=True, silent=True)

		selectedLines	= [ line for line in lines if re.search(reWhere, line) ]
		accessors		= []

		for selectedLine in selectedLines:
			m = re.match(reSelect, selectedLine)

			if m is not None:
				accessors.append(re.match(reSelect, selectedLine).group(1).strip())

		selectedValues	= {}

		for accessor in accessors:
			value = self.getValue(ref=ref, accessor=accessor)
			accessor = accessor[ 0 : -1 ] if accessor.endswith('/') else accessor
			selectedValues[accessor] = value

		if sort is True:
			selectedValues = { element[0] : element[1]
				for element in sorted(list(selectedValues.items()), key=lambda key : len(key[0]), reverse=True) }

		return selectedValues
	#___________________________________________________________________________
	#
	def concatAccessors(self, accessors, exists):
		pass
	#___________________________________________________________________________
	#
	def showValue(self, ref=None, accessor='.', showEmpty=True, silent=False):

		lines = []

		def outputMap(map, name=None, path='.'):

			nb = 0
			indexLineNb = len(lines)

			for key, value in map.items():
				isShown = outputValue(value, name=key, path='%s/%s' % (path, key))

				if isShown is True:
					nb += 1

			if showEmpty is False and nb == 0:
				return False

			lines.insert(indexLineNb, '%s (%s) {* : %s' % (path, type(map).__name__, nb))

			return True

		def outputArray(array, name=None, path='.'):

			nb = 0
			indexLineNb = len(lines)

			for i, value in enumerate(array):
				isShown = outputValue(value, name=i, path='%s/%s' % (path, i))

				if isShown is True:
					nb += 1

			if showEmpty is False and nb == 0:
				return False

			lines.insert(indexLineNb, '%s (%s) [* : %s' % (path, type(array).__name__, nb))

			return True

		def outputScalar(scalar, name=None, path='.'):

			if showEmpty is False and (scalar is None or scalar is False):
				return False

			lines.append('%s (%s) : %s' % (path, type(scalar).__name__, scalar))

			return True

		def outputValue(value, name=None, path='.'):

			if isinstance(value, dict):
				isShown = outputMap(value, path=path)
			elif isinstance(value, list):
				isShown = outputArray(value, path=path)
			else:
				isShown = outputScalar(value, path=path)

			return isShown

		value = self.getValue(ref=ref, accessor=accessor)
		outputValue(value)

		if silent is False:
			print()
			print('\n'.join(lines))

		return lines
