from AbstractGenerator import AbstractGenerator

import re
import os
import shutil

class CodeGenerator(AbstractGenerator):

	participants			= None
	currentClassId			= None
	currentImplementation	= None
	indent					= None
	importClasses			= None

	@classmethod
	def reset(cls):

		cls.participants			= {}
		cls.currentImplementation	= None
		cls.indent					= 2
		cls.importClasses			= []
	#___________________________________________________________________________
	#
	@classmethod
	def generate(cls, example):

		cls.reset()

		outputDir = './code-GEN'

		cls.generateClassesScenariosChunks(example)	# En 1er: pour obtenir cls.participants
		cls.generateClassesChunks(example)
		cls.generateCode(example, outputDir)

		cls.reset()
	#___________________________________________________________________________
	#
	@classmethod
	def generateClassesChunks(cls, example):

		modelClasses = example.findAll(select='.+/generation\.model\.Class::.+/', where='@class .+ generation\.model\.Class')

		for modelClass in modelClasses.values():
			classExtends= example.getValue(modelClass, './@extends')
			classId		= example.getValue(modelClass, './id')
			className	= example.getValue(modelClass, './name')
			attributes	= example.getValue(modelClass, './attributes')
			relations	= example.getValue(modelClass, './relations')
			methods		= example.getValue(modelClass, './methods')

			ref	 = example.getValue('generation.source.Chunks::%s' % classId, default=None)

			if ref is None:
				ref = example.setObject({ '@class' : 'generation.source.Chunks',
						'id' : classId
					})

			cls.currentClassId = classId
			cls.importClasses = []

			example.setValue(ref, './class/imports/lines', [])

			shortClassExtends = ''
			callParentConstructor = ''

			if classExtends is not None:
				cls.importClasses.append(classExtends)

				sClassExtends		= '.' if classExtends is None else classExtends
				shortClassExtends	= sClassExtends[ sClassExtends.rindex('.') + 1 : ]

				###
				### FIXME: Externaliser les paramètres spécifiques de constructeurs...
				###
				parentConstructorParameters = '[]' if shortClassExtends == 'QApplication' else ''
				callParentConstructor = '		super().__init__(%s)' % parentConstructorParameters

			example.setValue(ref, './class/begin/lines', [
					'class %s(%s):' % (className, shortClassExtends),
				])

			example.setValue(ref, './class/__init__/begin/lines', [
					'',
					'	def __init__(self):',
				])
			example.setValue(ref, './class/__init__/beforeCallSuper/attributes', {})
			example.setValue(ref, './class/__init__/beforeCallSuper/relations', {})

			callSuperLines = [
				callParentConstructor,
			]

			if callParentConstructor != '':
				callSuperLines.append('')

			example.setValue(ref, './class/__init__/callSuper/lines', callSuperLines)

			for attribute in attributes:
				attributeId		= example.getValue(attribute, './id')
				attributeName	= example.getValue(attribute, './name')
				attributeType	= example.getValue(attribute, './type')
				attributeValue	= example.getValue(attribute, './value')
				beforeAnyOperation	= example.getValue(attribute, './@beforeAnyOperation')

				if beforeAnyOperation is True:
					example.setValue(ref, './class/__init__/beforeCallSuper/attributes/%s/lines' % attributeId, [
							'		self.%s = %s' % (attributeName, attributeValue),
						])
				else:
					example.setValue(ref, './class/__init__/attributes/%s/lines' % attributeId, [
							'		self.%s = %s' % (attributeName, attributeValue),
						])

			for relation in relations:
				relationId    = example.getValue(relation, './id')
				relationName  = example.getValue(relation, './name')
				relationType  = example.getValue(relation, './type')
				relationValue = example.getValue(relation, './value')

				beforeAnyOperation	= example.getValue(relation, './@beforeAnyOperation', default=False)
				instantiate	= example.getValue(relation, './@instantiate', default=False)

				if instantiate is True:
					cls.importClasses.append(relationType)
					relationValue = '%s()' % relationType[ relationType.rindex('.') + 1 : ]

				if beforeAnyOperation is True:
					example.setValue(ref, './class/__init__/beforeCallSuper/relations/%s/lines' % relationId, [
							'		self.%s = %s' % (relationName, relationValue),
						])
				else:
					example.setValue(ref, './class/__init__/relations/%s/lines' % relationId, [
							'		self.%s = %s' % (relationName, relationValue),
						])

			constructorId = None

			for method in methods:
				methodId	= example.getValue(method, './id')
				methodName	= example.getValue(method, './name')
				parameters	= example.getValue(method, './parameters', default={})
				methodIsStatic = example.getValue(method, './static')
				methodIsConstructor = example.getValue(method, './isConstructor')

				annotation = '	@classmethod' if methodIsStatic is True else ''
				firstParam = 'cls' if methodIsStatic is True else 'self'

				callParentConstructor = ''

				if methodIsConstructor is True:
					constructorId = methodId
					methodName = '__init__'
					callParentConstructor = '		super().__init__()'

					extendsClassModelObject = example.getValue('generation.model.Class::%s' % classExtends, default=None)

					if extendsClassModelObject is not None:
						methsWithId = example.findAll(ref=extendsClassModelObject, select='.+/',
							where='./methods/.+/id .+ %s' % example.noRegExp(classExtends))

						if len(methsWithId) > 0:
							parentConstructor = list(methsWithId.values())[0]
							constructorParameters = example.getValue(parentConstructor, './parameters', default={})

							parametersAsStr = ', '.join([
								'%s' % example.getValue(parameter, 'name')
									for parameter in constructorParameters.values() ])

							callParentConstructor = '		super().__init__(%s)' % parametersAsStr

				parametersAsStr = ', '.join([
					'%s' % example.getValue(parameter, 'name')
						for parameter in parameters.values() ])
				virgule = '' if len(parameters) == 0 else ', '

				lines = [
						annotation,
						'	def %s(%s%s%s):' % (methodName, firstParam, virgule, parametersAsStr),
						callParentConstructor,
					]

				if methodIsStatic is True:
					lines.insert(0, '')

				if callParentConstructor != '':
					lines.append('')

				example.setValue(ref, './class/methods/%s/begin/lines' % methodId, lines)

				qualifiedMethodId = '%s::%s' % (classId, methodId)

				operations = example.findAll(select='.+/operations/\d+/', where='methodId .+ %s' % example.noRegExp(qualifiedMethodId))
				implementation = {}
				bodyLines = []
				rang = None

				for i, operation in enumerate(operations.values()):
					impl = example.getValue(operation, '?/operations', default={})

					if len(impl) > 0:
						implementation = impl
						rang = i

				if len(implementation) > 0:
					accessor = list(operations.keys())[rang]
					participantsAccessor = '%s/participants' % re.search(r'.+?/.+?/', accessor).group(0)

					cls.participants = {
							participant : example.getValue(modelObject, './class')
								for participant, modelObject in example.getValue(accessor=participantsAccessor).items()
						}
					bodyLines = cls.manageImplementation(example, implementation, lines=[])
				else:
					srcCodeRef = 'input.source.Code::%s' % classId
					srcCodeAccessor = './methods/%s' % methodId

					srcCode = example.getValue(srcCodeRef, srcCodeAccessor, default=None)

					if srcCode is not None:
						imports = example.getValue(srcCode, './imports/lines')
						bodyLines = example.getValue(srcCode, './body/lines')

						if len(imports) > 0:
							importLines = example.getValue(ref, './class/imports/lines')

							importLines.extend(imports)
							importLines = list(set(importLines))

							example.setValue(ref, './class/imports/lines', importLines)

				if len(bodyLines) == 0:
					if not methodIsConstructor:
						example.setValue(ref, './class/methods/%s/end/lines' % methodId, [
								'		pass',
							])
				else:
					example.setValue(ref, './class/methods/%s/body/lines' % methodId, bodyLines)

			if constructorId is not None:
				# On déplace ce qui a été stocké sous ./class/__init vers ./class/methods/constructorId
				example.setValue(ref, './class/methods/%s/attributes' % constructorId,
					example.getValue(ref, './class/__init__/attributes', default={}))
				example.setValue(ref, './class/methods/%s/relations' % constructorId,
					example.getValue(ref, './class/__init__/relations', default={}))
				example.setValue(ref, './class/__init__', {})

			if len(attributes) + len(relations) == 0:
				if constructorId is None:
					example.setValue(ref, './class/__init__/end/lines', [
							'		pass',
						])
				else:
					example.setValue(ref, './class/methods/%s/end/lines' % constructorId, [
							'		pass',
						])

			if len(cls.importClasses) > 0:
				packages = [
						importClass[ 0 : importClass.rindex('.') ]
							for importClass in cls.importClasses
								if not importClass.startswith('.')
					]
				shortClasses = [ importClass[ importClass.rindex('.') + 1 : ] for importClass in sorted(cls.importClasses) ]

				sysPathAppends	= list(set([ "sys.path.append('./code-GEN/%s')" % package.replace('.', '/') for package in packages ]))
				fromImports		= list(set([ 'from %s import %s' % (classe, classe) for classe in shortClasses ]))

				imports = example.getValue(ref, './class/imports/lines')

				if len(sysPathAppends) > 0:
					imports.append('import sys')
					imports.append('')
					imports.extend(sysPathAppends)
					imports.append('')

				if len(fromImports) > 0:
					imports.extend(fromImports)
					imports.append('')

					if classExtends is not None and classExtends.startswith('.'):
						###
						### FIXME: externaliser les remplacements...
						###
						example.setValue(ref, './replacements/from QApplication import', 'from PyQt5.QtWidgets import')
						example.setValue(ref, './replacements/from QMainWindow import', 'from PyQt5.QtWidgets import')
						example.setValue(ref, './replacements/from QStackedWidget import', 'from PyQt5.QtWidgets import')
						example.setValue(ref, './replacements/from QWidget import', 'from PyQt5.QtWidgets import')
	#___________________________________________________________________________
	#
	@classmethod
	def generateClassesScenariosChunks(cls, example):

		scenariosConception = example.findAll(select='.+/conception\.Scenario::.+/', where='@class .+ conception\.Scenario')

		# Pour chaque scénario

		for n, scenario in enumerate(scenariosConception.values(), 1):
			classe = 'test.scenario.Scenario%s' % n

			ref = example.getValue('generation.source.Chunks::%s' % classe, default=None)

			if ref is None:
				ref = example.setObject({ '@class' : 'generation.source.Chunks',
						'id' : classe
					})

			example.setValue(ref, './class/imports/lines', [])
			example.setValue(ref, './class/begin/lines', [
					'class Scenario%s():' % n,
				])
			example.setValue(ref, './class/__init__/begin/lines', [
					'',
					'	def __init__(self):',
					'',
				])
			example.setValue(ref, './class/__init__/end/lines', [
					'		pass',
				])
			example.setValue(ref, './class/methods/test()/begin/lines', [
					'',
					'	def test(self):',
					'',
				])
			example.setValue(ref, './class/__main__/begin/lines', [
					'',
					'Scenario%s().test()' % n,
				])

			participants = example.getValue(scenario, './participants')

			for name, participant in participants.items():
				classe	= example.getValue(participant, './class')

				cls.participants[name] = classe

			interactions = example.getValue(scenario, './extend/interactions')

			for i, interaction in enumerate(interactions):
				itrId = example.getValue(interaction, '?/id', default=None)
				inputs = example.getValue(interaction, '?/inputs', default={})
				outputs = example.getValue(interaction, '?/outputs', default={})

				displayInputs = [ '		print(">>> [INPUT ] %s=%s")' % (key, value)
									for key, value in inputs.items() ]
				displayOutputs = [ '		print(">>> [OUTPUT] %s=%s" %% %s)' % (key, '%s', key)
									for key, value in outputs.items() ]
				assertOutputs = [ '		assert %s == %s, "VALEUR ATTENDUE: %s=%s / Valeur obtenue: %s=%s" %% %s' % (
					key, value,
					key, value,
					key, '%s', key) for key, value in outputs.items() ]

				if len(displayInputs) > 0:
					example.setValue(ref, './class/methods/test()/interaction-%d/inputs/lines' % i, displayInputs)

				if len(displayOutputs) > 0:
					example.setValue(ref, './class/methods/test()/interaction-%d/outputs/lines' % i, displayOutputs)

				if len(assertOutputs) > 0:
					example.setValue(ref, './class/methods/test()/interaction-%d/asserts/lines' % i, assertOutputs)

				if itrId is not None:
					beforeOperations = example.getValue(scenario, './before/%s/operations' % itrId, default=[])
					afterOperations = example.getValue(scenario, './after/%s/operations' % itrId, default=[])

					operations = beforeOperations
					operations.extend(afterOperations)

					participants = cls.findParticipants(example, operations)

					packages = [ participant[ 0 : participant.rindex('.') ] for participant in participants ]
					shortClasses = [ participant[ participant.rindex('.') + 1 : ] for participant in participants ]

					sysPathAppends	= [ "sys.path.append('./code-GEN/%s')" % package.replace('.', '/') for package in packages ]
					fromImports		= [ 'from %s import %s' % (classe, classe) for classe in shortClasses ]

					imports = example.getValue(ref, './class/imports/lines')

					if len(sysPathAppends) > 0:
						imports.append('import sys')
						imports.append('')
						imports.extend(sysPathAppends)
						imports.append('')

					if len(fromImports) > 0:
						imports.extend(fromImports)
						imports.append('')

					methodTestBodyLines = example.getValue(ref, './class/methods/test()/body/lines', default=[], setDefault=True)

					methodTestBodyLines.extend(cls.manageOperations(example, operations, lines=[]))
	#___________________________________________________________________________
	#
	@classmethod
	def findParticipants(cls, example, operations):

		participants = []

		for operation in operations:
			name = example.getValue(operation, '?/name')

			if name == 'New':
				participant = example.getValue(operation, '?/participant')
				classe = cls.participants[participant]

				if classe not in participants:
					participants.append(classe)

		return participants
	#___________________________________________________________________________
	#
	@classmethod
	def manageImplementation(cls, example, implementation, lines=[]):

		cls.currentImplementation = implementation

		cls.manageOperations(example, implementation, lines)

		return lines
	#___________________________________________________________________________
	#
	@classmethod
	def manageOperations(cls, example, operations, lines=[]):

		for operation in operations:
			name = example.getValue(operation, '?/name')
			eval('cls.manageOp%s(example, operation, lines)' % name)

		return lines
	#___________________________________________________________________________
	#
	@classmethod
	def manageOpNew(cls, example, operation, lines):

		participant	= example.getValue(operation, '?/participant')
		instance	= example.getValue(operation, '?/instance', default=participant)
		parameters	= example.getValue(operation, '?/parameters', default={})

		classe = cls.participants[participant]

		constructor = classe[ classe.rindex('.') + 1 : ]
		paramsValues = ', '.join([
			'%s' % (
				str(example.getValue(parameter, './value')
					).replace('}}', ''
					).replace('{{', ''
					).replace('this', 'self'
					).replace('super', 'super()'
					)
			)
				for name, parameter in parameters.items() ])

		instance = '' if instance is None else instance
		instance = re.sub(r'^this(\.|$)', r'self\1', instance)
		affectation = ''

		if instance != '':
			affectation = '%s = ' % instance

		lines.append('%s%s%s(%s)' % ('\t' * cls.indent, affectation, constructor, paramsValues))

		if classe != cls.currentClassId:
			cls.importClasses.append(classe)
	#___________________________________________________________________________
	#
	@classmethod
	def manageOpDefine(cls, example, operation, lines):

		# NOOP: car Define ne génère rien dans une implémentation
		pass
	#___________________________________________________________________________
	#
	@classmethod
	def manageOpCall(cls, example, operation, lines):

		returnedVar		= example.getValue(operation, '?/returnedVar', default=None)
		participant		= example.getValue(operation, '?/participant')
		instance		= example.getValue(operation, '?/instance', default=participant)
		method			= example.getValue(operation, '?/method')
		parameters		= example.getValue(operation, '?/parameters', default={})
		implementation	= example.getValue(operation, '?/operations', default=[])

		classe = cls.participants[participant]
		isStatic = instance[0 : 1] == instance[0 : 1].upper()

		paramsValues = ', '.join([
			'%s' % (
				str(example.getValue(parameter, './value', default=None)
					).replace('}}', ''
					).replace('{{', ''
					).replace('this', 'self'
					).replace('super', 'super()'
					)
			)
				for name, parameter in parameters.items() ])

		instance	= re.sub(r'^this(\.|$)', r'self\1', instance)
		instance	= re.sub(r'^(super)(\.|$)', r'\1()\2', instance)
		returnedVar = '' if returnedVar is None else returnedVar
		affectation = ''

		if returnedVar != '':
			affectation = '%s = ' % returnedVar

		lines.append('%s%s%s.%s(%s)' % ('\t' * cls.indent, affectation, instance, method, paramsValues))

		if classe != cls.currentClassId and isStatic is True:
			cls.importClasses.append(classe)
	#___________________________________________________________________________
	#
	@classmethod
	def manageOpIf(cls, example, operation, lines):

		condition	= example.getValue(operation, '?/condition'
			).replace('}}', ''
			).replace('{{', ''
			).replace('this', 'self'
			).replace('super', 'super()'
			)
		Then		= example.getValue(operation, '?/then/operations')
		Else		= example.getValue(operation, '?/else/operations', default={})

		lines.append('%sif %s:' % ('\t' * cls.indent, condition))

		if len(Then) > 0:
			cls.indent += 1
			cls.manageImplementation(example, Then, lines)
			cls.indent -= 1

		if len(Else) > 0:
			lines.append('%selse:' % ('\t' * cls.indent))
			cls.indent += 1
			cls.manageImplementation(example, Else, lines)
			cls.indent -= 1
	#___________________________________________________________________________
	#
	@classmethod
	def manageOpFor(cls, example, operation, lines):

		item	= example.getValue(operation, '?/item')
		In		= example.getValue(operation, '?/in')
		In		= In.replace('this', 'self'
			).replace('super', 'super()'
			)
		do		= example.getValue(operation, '?/do/operations')

		lines.append('%sfor %s in %s:' % ('\t' * cls.indent, item, In))

		if len(do) > 0:
			cls.indent += 1
			cls.manageImplementation(example, do, lines)
			cls.indent -= 1
	#___________________________________________________________________________
	#
	@classmethod
	def manageOpSet(cls, example, operation, lines):

		var		= example.getValue(operation, '?/var'
			).replace('this', 'self'
			)
		value	= str(example.getValue(operation, '?/value'
			)).replace('}}', ''
			).replace('{{', ''
			).replace('this', 'self'
			).replace('super', 'super()'
			)
		lines.append('%s%s = %s' % ('\t' * cls.indent, var, value))
	#___________________________________________________________________________
	#
	@classmethod
	def manageOpReturn(cls, example, operation, lines):

		value = example.getValue(operation, '?/value'
			).replace('}}', ''
			).replace('{{', ''
			).replace('this', 'self'
			).replace('super', 'super()'
			)
		lines.append('%sreturn %s' % ('\t' * cls.indent, value))
	#___________________________________________________________________________
	#
	@classmethod
	def manageOpRaise(cls, example, operation, lines):

		exception	= example.getValue(operation, '?/exception')
		message		= example.getValue(operation, '?/message')
		parameters	= example.getValue(operation, '?/parameters')

		paramsValues = ', '.join([
			'%s' % (
				str(parameter
					).replace('}}', ''
					).replace('{{', ''
					).replace('this', 'self'
					).replace('super', 'super()'
					)
			)
				for parameter in parameters ])

		lines.append('%sraise ValueError("[%s] %s" %% (%s))' % ('\t' * cls.indent, exception, message, paramsValues))
	#___________________________________________________________________________
	#
	@classmethod
	def manageOpNoop(cls, example, operation, lines):

		lines.append('%spass	# NOOP' % ('\t' * cls.indent))
	#___________________________________________________________________________
	#
	@classmethod
	def manageOpCode(cls, example, operation, lines):

		codeLines = example.getValue(operation, '?/lines')

		lines.extend(codeLines)
	#___________________________________________________________________________
	#
	@classmethod
	def generateCode(cls, example, codeGenDir):

		existsDir = os.path.exists(codeGenDir)

		if existsDir is True and codeGenDir.endswith('/code-GEN'):
			shutil.rmtree(codeGenDir)
		os.makedirs(codeGenDir)

		srcChunks = example.findAll(select='.+/generation\.source\.Chunks::.+/', where='@class .+ generation\.source\.Chunks')

		# Pour chaque source chunk

		for srcChunk in srcChunks.values():
			# On récupère les lignes du source complet

			selection = example.findAll(ref=srcChunk, select='.+/lines', where='/lines ')

			lines = [ element for sublist in selection.values() for element in sublist ]
			source = '%s\n' % '\n'.join(lines)

			# On effectue les éventuels remplacements

			replacements = example.getValue(srcChunk, './replacements', default={})

			for replacement in replacements:
				source = source.replace(replacement, replacements[replacement])

			# On écrit le source dans le fichier de sortie

			classe = example.getValue(srcChunk, './id')

			p = classe.rindex('.')
			package = classe[ 0 : p ]
			name = classe[ p + 1 : ]
			filedir = '%s/%s' % (codeGenDir, package.replace('.', '/'))
			filename = '%s/%s.py' % (filedir, name)

			os.makedirs(filedir, exist_ok=True)

			with open(filename, 'w') as f:
				f.write(source)
