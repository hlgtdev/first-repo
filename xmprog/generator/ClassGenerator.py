from AbstractGenerator import AbstractGenerator

import re

class ClassGenerator(AbstractGenerator):

	@classmethod
	def reset(cls):

		pass
	#___________________________________________________________________________
	#
	@classmethod
	def generate(cls, example):

		cls.reset()

		cls.preProcess(example)
		cls.generateClassesProperties(example)
		cls.generateClassesMethods(example)
		cls.generateClassesMethodsFromCode(example)

		cls.reset()
	#___________________________________________________________________________
	#
	@classmethod
	def preProcess(cls, example):

		# Evaluation des REFérences

		refAccessors = example.findAll(select='.+/.+? ', where='REF=')

		for refAccessor in refAccessors:
			sRef = example.getValue(accessor=refAccessor)

			if isinstance(sRef, str) is not True:
				continue

			ref = sRef.split('=')[1]

			refValue = example.getValue(ref=ref)
			example.setValue(accessor=refAccessor, value=refValue)

		# Ajout de l'entrée /name pour les participants

		participants = example.findAll(select='.+/participants/.+?/', where='/participants')

		for accessor, participant in participants.items():
			newPart = { 'name' : accessor[ accessor.rindex('/') + 1 : ] }
			newPart.update(participant)
			example.setValue(accessor=accessor, value=newPart)

		# Ajout de l'entrée /name pour les interactions et suppression de l'entrée constituée du nom de l'interaction

		interactionsLists = example.findAll(select='.+/interactions', where='interactions/', sort=True)

		for accessor, interactionsList in interactionsLists.items():
			if '/extend/' in accessor:
				continue

			for i, interaction in enumerate(interactionsList):
				typ = list(interaction.keys())[0]
				newInteraction = { 'type' : typ }
				newInteraction.update(interaction[typ])
				interactionsList[i][typ] = newInteraction

		# Evaluation & ajout de l'entrée /methodId

		meths = example.findAll(select='.+/', where='operations/.+/method ')

		for methAccessor, meth in meths.items():
			if methAccessor.endswith('/rest'):
				continue

			participant = example.getValue(meth, './participant')
			method = example.getValue(meth, './method')
			parameters = example.getValue(meth, './parameters', default={})

			participantsAccessor = '%s/participants' % methAccessor[ 0 : methAccessor.rindex('/after') ]

			participants = example.getValue(accessor=participantsAccessor)
			classe = example.getValue(participants, '%s/class' % participant)

			methodId = '%s(%s)' % (method, ', '.join([
				'%s: %s' % (
						name,
						example.getValue(parameter, 'type') if type(example.getValue(parameter, 'type')).__name__ == 'str'
							else example.getValue(parameter, 'type').__name__
				)
					for name, parameter in parameters.items() ]))

			newMeth = { 'methodId' : '%s::%s' % (classe, methodId) }
			newMeth.update(meth)
			example.setValue(accessor=methAccessor, value=newMeth)

		# ajout de l'entrée /operations après les conteneurs implicites d'opération: do, then, else, ...

		operationsSelfContainers = example.findAll(select='.+/(do|then|else)', where='operations/.+/(do|then|else)/', sort=True)

		for accessor, operationsSelfContainer in operationsSelfContainers.items():
			operations = { 'operations' : operationsSelfContainer }
			example.getValue(accessor=accessor)
			example.setValue(accessor=accessor, value=operations)

		# Ajout de l'entrée /name pour les opérations et suppression de l'entrée constituée du nom de l'opération

		operationsLists = example.findAll(select='.+/operations', where='operations/', sort=True)

		for operationsList in operationsLists.values():
			for i, operation in enumerate(operationsList):
				name = list(operation.keys())[0]
				newOperation = { 'name' : name }
				newOperation.update(operation[name])
				operationsList[i][name] = newOperation
	#___________________________________________________________________________
	#
	@classmethod
	def generateClassesProperties(cls, example):

		modelObjects = example.findAll(select='.+/%s\..+::.+/' % example.rootPackage, where='@class .+ %s\.' % example.rootPackage)

		modelObjects.update(example.findAll(select='.+/test\..+::.+/', where='@class .+ test\.'))

		for accessor, modelObject in modelObjects.items():
			finalValues = example.getValue(modelObject, './@finalValues', default=False)
			classe = example.getValue(modelObject, './@class')
			ref = example.getValue('generation.model.Class::%s' % classe, default=None)

			if ref is None:
				p = classe.rindex('.')
				package = classe[ 0 : p ]
				className = classe[ p + 1 : ]

				ref = example.setObject({ '@class' : 'generation.model.Class',
						'@extends' 		: None,
						'@abstract'     : False,
						'id' 			: classe,
						'name'          : className,
						'package'       : package,
						'attributes'    : [],
						'relations'     : [],
						'methods'       : [],
					})

			for prop, value in modelObject.items():
				if prop.startswith('@'):
					if prop in ('@abstract', '@extends'):
						example.setValue(ref, './%s' % prop, value)
					continue

				beforeAnyOperation = False
				instantiate = False

				if isinstance(value, dict):
					beforeAnyOperation = example.getValue(value, '@beforeAnyOperation', default=False)
					instantiate = example.getValue(value, '@instantiate', default=False)

				v, typ, subType, displaySubType = cls.getPropertyDefinition(example, prop, value, finalValues)

				id = '%s: %s%s' % (prop, typ if isinstance(typ, str) else typ.__name__, displaySubType)

				elements = (example.getValue(ref, './relations', default=[]) if isinstance(typ, str) or isinstance(subType, str)
					else example.getValue(ref, './attributes', default=[]))

				attrsOrRelsWithId = example.findAll(ref=ref, select='.+/', where='id .+ %s' % example.noRegExp(id))

				if len(attrsOrRelsWithId) > 0:
					# Si l'id existe déjà, on passe au suivant
					continue

				nbElements	= len(elements)

				example.setValue(elements, './%d/id' % nbElements, id)
				example.setValue(elements, './%d/name' % nbElements, prop)
				example.setValue(elements, './%d/type' % nbElements, typ)
				example.setValue(elements, './%d/subType' % nbElements, subType)
				example.setValue(elements, './%d/value' % nbElements, v)
				example.setValue(elements, './%d/@showValue' % nbElements, finalValues)
				example.setValue(elements, './%d/@beforeAnyOperation' % nbElements, beforeAnyOperation)
				example.setValue(elements, './%d/@instantiate' % nbElements, instantiate)

			### Post-traitement sur la classe générée

			genClassAttrs = example.getValue(ref, './attributes')

			for i, genClassAttr in enumerate(genClassAttrs):
				id		= example.getValue(genClassAttr, './id')
				name	= example.getValue(genClassAttr, './name')
				typ		= example.getValue(genClassAttr, './type')

				if typ == type(None):
					# Si on a un attribut de type NoneType
					relsWithSameName = example.findAll(ref=ref, select='.+/', where='relations/.+/name .+ %s' % example.noRegExp(prop))

					if len(relsWithSameName) > 0:
						# Si une relation existe avec le même nom, on supprime l'attribut
						deletedAttrs = example.getValue(ref, './deleted/attributes', default=[])
						nbDeletedAttrs = len(deletedAttrs)

						example.setValue(ref, './deleted/attributes/%d' % nbDeletedAttrs, genClassAttr)
						genClassAttrs.pop(i)
	#___________________________________________________________________________
	#
	@classmethod
	def getPropertyDefinition(cls, example, prop, value, finalValues=False):

		v = value
		typ = type(v)
		subType = None

		if isinstance(value, list):
			if finalValues is False:
				v = []

			if len(value) > 0:
				firstElement = value[0]

				if isinstance(firstElement, dict) and '@class' in firstElement:
					subType = example.getValue(firstElement, './@class')
				else:
					subType = type(firstElement)
		elif isinstance(value, dict):
			typ = example.getValue(value, './@class') if '@class' in value else typ
			id = '%s: %s' % (prop, typ if isinstance(typ, str) else typ.__name__)

			if finalValues is False:
				v = None if '@class' in value else {}

			###
			### FIXME: gérer keySubType & valueSubType...
			###

			if len(value) > 0:
				firstElement = list(value.values())[0]

				if isinstance(firstElement, dict) and '@class' in firstElement:
					subType = example.getValue(firstElement, './@class')
				else:
					subType = type(firstElement)
		else:
				try:
					if finalValues is False:
						v = eval("%s()" % typ.__name__)

					v = '"%s"' % v.replace('"', '\"') if typ == str else v
				except:
					v = None

		displaySubType = ''

		if subType is not None:
			displaySubType = '<%s>' % (subType if isinstance(subType, str) else subType.__name__)

		return v, typ, subType, displaySubType
	#___________________________________________________________________________
	#
	@classmethod
	def generateClassesMethods(cls, example):

		scenariosConception = example.findAll(select='.+/conception\.Scenario::.+/', where='@class .+ conception\.Scenario')

		# Pour chaque scénario

		for scenario in scenariosConception.values():
			id = example.getValue(scenario, './id')
			participants = example.getValue(scenario, './participants')

			# Stockage d'une nouvelle classe par participant

			for name, participant in participants.items():
				classe = example.getValue(participant, './class')
				ref = example.getValue('generation.model.Class::%s' % classe, default=None)
				rest = example.getValue(participant, './rest', default=None)

				if ref is None:
					p = classe.rindex('.')
					package = classe[ 0 : p ]
					className = classe[ p + 1 : ]

					ref = example.setObject({ '@class' : 'generation.model.Class',
							'@extends' 		: None,
							'@abstract'     : False,
							'id' 			: classe,
							'name'          : className,
							'package'       : package,
							'rest'       	: rest,
							'attributes'    : [],
							'relations'     : [],
							'methods'       : [],
						})
				else:
					example.setValue(ref, './rest', value=rest)

			# Pour chaque opération

			operations = example.findAll(scenario, select='.+/operations/\d+', where='/operations/')

			for accessor, operation in operations.items():
				name = example.getValue(operation, '?/name')

				accessorAt  = '%s/participant' % accessor[ 0 : accessor.rindex('/operations') ]
				at = example.getValue(scenario, accessorAt, default=None)

				if at is not None and at != 's':
					atClass = example.getValue(participants, './%s/class' % at)
					atClassModelObject = example.getValue('generation.model.Class::%s' % atClass)

				attributesCandidates	= []
				relationsCandidates		= []

				if name in ('Define', 'Call', 'New'):
					participant     = example.getValue(operation, '?/participant')
					operationClass	= example.getValue(participants, './%s/class' % participant)
					operationClassName	= operationClass[ operationClass.rindex('.') + 1 : ]
					instance        = example.getValue(operation, '?/instance', default=participant)
					rest		    = example.getValue(operation, '?/rest', default=None)
					method          = example.getValue(operation, '?/method', default=operationClassName)
					typ          	= example.getValue(operation, '?/type', default=None)
					isConstructor   = example.getValue(operation, '?/isConstructor', default=method == operationClassName)
					parameters      = example.getValue(operation, '?/parameters', default={})

					if at is not None and at != 's':
						# On garde l'éventuelle relation d'appel de méthode
						mRelationAttr = re.match(r'^this\.(\w+)$', instance)

						if mRelationAttr is not None:
							relationsCandidates.append( (mRelationAttr.group(1), operationClass) )

					# Stockage de la méthode si elle n'existe pas déjà

					methodId = '%s(%s)' % (method, ', '.join([
						'%s: %s' % (
								name,
								example.getValue(parameter, 'type') if type(example.getValue(parameter, 'type')).__name__ == 'str'
									else example.getValue(parameter, 'type').__name__
						)
							for name, parameter in parameters.items() ]))

					operationClassModelObject = example.getValue('generation.model.Class::%s' % operationClass)

					methsWithId = example.findAll(ref=operationClassModelObject, select='.+/',
						where='./methods/.+/id .+ %s' % example.noRegExp(methodId))

					if len(methsWithId) > 0:
						# Si la méthode existe déjà dans la classe
						continue

					operationClassExtends = example.getValue(operationClassModelObject, './@extends')

					if operationClassExtends is not None:
						extendsClassModelObject = example.getValue('generation.model.Class::%s' % operationClassExtends, default=None)

						if extendsClassModelObject is not None:
							methsWithId = example.findAll(ref=extendsClassModelObject, select='.+/',
								where='./methods/.+/id .+ %s' % example.noRegExp(methodId))

							if name != 'Define' and len(methsWithId) > 0:
								# Si la méthode n'est pas une définition et qu'elle existe déjà dans la classe parente
								continue

					refClass = 'generation.model.Class::%s' % operationClass

					isStatic = instance[0 : 1] == instance[0 : 1].upper()
					staticMethod = '@staticmethod' if isStatic else ''

					objMethods = example.getValue(refClass, './methods')
					nbMethods = len(objMethods)

					example.setValue(objMethods, './%d/id' % nbMethods, methodId)
					example.setValue(objMethods, './%d/static' % nbMethods, isStatic)
					example.setValue(objMethods, './%d/isConstructor' % nbMethods, isConstructor)
					example.setValue(objMethods, './%d/rest' % nbMethods, rest)
					example.setValue(objMethods, './%d/name' % nbMethods, method)
					example.setValue(objMethods, './%d/type' % nbMethods, typ)

					for name, parameter in parameters.items():
						typ = example.getValue(parameter, './type')
						parameterValue = example.getValue(parameter, './value', default=None)
						parameterValue = str(parameterValue
							).replace('}}', ''
							).replace('{{', ''
							)
						mAttrOrRel = re.match(r'^this\.(\w+)$', parameterValue)

						if mAttrOrRel is not None:
							attrOrRel = mAttrOrRel.group(1)

							if isinstance(typ, str) is True:
								relationsCandidates.append( (attrOrRel, typ) )
							else:
								attributesCandidates.append( (attrOrRel, typ) )

						example.setValue(objMethods, './%d/parameters/%s/name' % (nbMethods, name), name)
						example.setValue(objMethods, './%d/parameters/%s/type' % (nbMethods, name), typ)
				elif name in ('Set'):
					if at is not None and at != 's':
						var = example.getValue(operation, '?/var')
						typ = example.getValue(operation, '?/type', default=None)
						value = example.getValue(operation, '?/value')
						value = str(value
							).replace('}}', ''
							).replace('{{', ''
							)
						mAttrOrRel = re.match(r'^this\.(\w+)$', var)

						if mAttrOrRel is not None:
							attrOrRel = mAttrOrRel.group(1)

							if isinstance(typ, str) is True:
								relationsCandidates.append( (attrOrRel, typ) )
							else:
								attributesCandidates.append( (attrOrRel, typ) )

						mAttrOrRel = re.match(r'^this\.(\w+)$', value)

						if mAttrOrRel is not None:
							attrOrRel = mAttrOrRel.group(1)

							if isinstance(typ, str) is True:
								relationsCandidates.append( (attrOrRel, typ) )
							else:
								attributesCandidates.append( (attrOrRel, typ) )

				# On traite les éventuels attributs

				for attributeCandidate in attributesCandidates:
					attr	= attributeCandidate[0]
					typ		= attributeCandidate[1]

					attributeId = '%s: %s' % (attr, typ.__name__)

					attrsWithId = example.findAll(ref=atClassModelObject, select='.+/', where='id .+ %s' % example.noRegExp(attributeId))

					if len(attrsWithId) == 0:
						# Si l'id n'existe pas déjà, on stocke la relation
						attributes = example.getValue(atClassModelObject, './attributes')

						nbAttributes = len(attributes)

						example.setValue(attributes, './%d/id' % nbAttributes, attributeId)
						example.setValue(attributes, './%d/name' % nbAttributes, attr)
						example.setValue(attributes, './%d/type' % nbAttributes, typ)
						example.setValue(attributes, './%d/subType' % nbAttributes, None)
						example.setValue(attributes, './%d/value' % nbAttributes, None)
						example.setValue(attributes, './%d/@showValue' % nbAttributes, True)

				# On traite les éventuelles relations

				for relationCandidate in relationsCandidates:
					relationAttr = relationCandidate[0]
					relationType = relationCandidate[1]

					relationId = '%s: %s' % (relationAttr, relationType)

					relsWithId = example.findAll(ref=atClassModelObject, select='.+/', where='id .+ %s' % example.noRegExp(relationId))

					if len(relsWithId) == 0:
						# Si l'id n'existe pas déjà, on stocke la relation
						relations = example.getValue(atClassModelObject, './relations')

						atClassName = atClass[ atClass.rindex('.') + 1 : ]

						constructors = example.findAll(select='.+/', where='methods/\d+/name .+ %s' % example.noRegExp(atClassName))
						constructor = None if len(constructors) == 0 else list(constructors.values())[0]

						constructorParameters = example.getValue(constructor, './parameters', default={})

						# La valeur de l'attribut est celle de l'éventuel paramètre de même nom fourni au constructeur
						relationValue = relationAttr if relationAttr in constructorParameters else 'None'

						nbRelations = len(relations)

						example.setValue(relations, './%d/id' % nbRelations, relationId)
						example.setValue(relations, './%d/name' % nbRelations, relationAttr)
						example.setValue(relations, './%d/type' % nbRelations, relationType)
						example.setValue(relations, './%d/subType' % nbRelations, None)
						example.setValue(relations, './%d/value' % nbRelations, relationValue)
	#___________________________________________________________________________
	#
	@classmethod
	def generateClassesMethodsFromCode(cls, example):

		srcCodes = example.findAll(select='.+/', where='@class .+ input\.source\.Code')

		for srcCode in srcCodes.values():
			classId = example.getValue(srcCode, './id')
			methods = example.getValue(srcCode, './methods', default={})

			for methodId, method in methods.items():
				classModel = example.getValue(ref='generation.model.Class::%s' % classId, default=None)

				if classModel is None:
					# Si la classe dans le source n'existe pas dans le modèle, on l'ajoute
					package = classId[ 0 : classId.rindex('.') ]
					className = classId[ classId.rindex('.') + 1 : ]

					classModel = example.setObject({ '@class' : 'generation.model.Class',
							'@extends' 		: None,
							'@abstract'     : False,
							'id' 			: classId,
							'name'          : className,
							'package'       : package,
							'attributes'    : [],
							'relations'     : [],
							'methods'       : [],
						})

				classMethodsWithId = example.findAll(ref=classModel, select='.+/', where='methods/\d+/id .+ %s' % example.noRegExp(methodId))

				if len(classMethodsWithId) == 0:
					# Si la méthode dans le source n'existe pas dans la classe, on l'ajoute
					methods = example.getValue(classModel, './methods')
					nb = len(methods)

					name = re.sub(r'\(.*\)', r'', methodId)
					paramsAsString = re.sub(r'.*\(|\).*', r'', methodId)
					params = [ param for param in paramsAsString.split(', ') if param.strip() != '' ]

					parameters = {}

					example.setValue(classModel, './methods/%d/id' % nb, methodId)
					example.setValue(classModel, './methods/%d/static' % nb, False)
					example.setValue(classModel, './methods/%d/name' % nb, name)
					example.setValue(classModel, './methods/%d/isConstructor' % nb, False)
					example.setValue(classModel, './methods/%d/parameters' % nb, parameters)

					for param in params:
						T = param.split(':')
						paramName = T[0].strip()
						paramType = T[1].strip()

						try:
							paramType = eval(paramType)
						except:
							pass

						example.setValue(parameters, '%s/name' % paramName, paramName)
						example.setValue(parameters, '%s/type' % paramName, paramType)
