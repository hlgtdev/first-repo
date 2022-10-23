import os
XMPG_HOME = os.getenv('XMPG_HOME')

import sys
sys.path.append('%s/xmprog/core' % XMPG_HOME)
sys.path.append('%s/xmprog/generator' % XMPG_HOME)

from AbstractGenerator import AbstractGenerator

import re
import os
import shutil
import subprocess

class PlantumlGenerator(AbstractGenerator):

	PLANTUML_JAR	= '%s/lib/java/plantuml.1.2021.9.jar' % XMPG_HOME
	TAB				= '<color #green><size:10>**->| **</size></color>'

	participants	= None
	currentFrom		= None
	indent			= None
	#___________________________________________________________________________
	#
	@classmethod
	def reset(cls):

		cls.participants	= {}
		cls.currentFrom		= 's'
		cls.indent			= 0
	#___________________________________________________________________________
	#
	@classmethod
	def generate(cls, example, dryRun=False):

		cls.reset()

		outputDir = './output'
		fileradical = 'diagramme.Plantuml'
		lines = []

		lines.extend(cls.generateClassDiagram(example, fileradical))
		lines.extend(cls.generateAnalysis(example, fileradical))
		lines.extend(cls.generateDesign(example, fileradical))

		if dryRun is False:
			cls.generatePlantuml(lines, outputDir, fileradical)

		cls.reset()
	#___________________________________________________________________________
	#
	@classmethod
	def generateClassDiagram(cls, example, fileradical):

		svgFile = 'generation.conception.classe.%s.svg' % fileradical
		lines = []

		modelClasses = example.findAll(select='.+/generation\.model\.Class::.+/', where='@class .+ generation\.model\.Class')

		if len(modelClasses) > 0:
			ref = example.setObject({ '@class' : 'generation.conception.classe.diagramme.Plantuml',
					'id'		: 'DiagrammeClasseGlobal',
					'output'	: svgFile,
					'lines'		: lines,
				})

		lines.append("'%s" % (100 * '_'))
		lines.append("'")
		lines.append('@startuml %s' % svgFile)
		lines.append('title "Conception: Diagramme de classe global"')

		for modelClass in modelClasses.values():
			lines.append('')

			classExtends= example.getValue(modelClass, './@extends')
			isAbstract	= example.getValue(modelClass, './@abstract')
			classId		= example.getValue(modelClass, './id')
			className	= example.getValue(modelClass, './name')
			restPath	= example.getValue(modelClass, './rest/path', default=None)
			attributes	= example.getValue(modelClass, './attributes')
			relations	= example.getValue(modelClass, './relations')
			methods		= example.getValue(modelClass, './methods')

			abstract	= '' if isAbstract is False else 'abstract '
			shortClassExtends = classExtends[ classExtends.rindex('.') + 1 : ] if classExtends is not None and '.' in classExtends else classExtends
			stereotype = ''

			if classExtends is not None:
				stereotype += '%s' % shortClassExtends

			if restPath is not None:
				stereotype += 'REST: ' if stereotype == '' else ': '
				stereotype += '**%s**' % restPath

			if stereotype != '':
				stereotype = '<<%s>>' % stereotype

			lines.append("' CLASSE: %s" % className)
			lines.append('')
			lines.append('%sclass %s%s' % (abstract, classId, stereotype))
			lines.append('')

			for attribute in sorted(attributes, key=lambda attr: attr['id']):
				attributeId = example.getValue(attribute, './id')
				attributeValue = example.getValue(attribute, './value')
				showValue = example.getValue(attribute, './@showValue')

				value = ' = %s' % attributeValue if showValue is True else ''
				value = value.replace('None', 'null')

				lines.append('%s : - %s%s' % (classId, attributeId, value))

			if len(attributes) > 0:
				lines.append('')

			for method in sorted(methods, key=lambda meth: meth['id']):
				methodId = example.getValue(method, './id')

				rest = example.getValue(method, './rest')
				methodIsStatic = example.getValue(method, './static')
				typ = example.getValue(method, './type')

				restMethodAndPath = '' if rest is None else '//<<REST>> **%s %s**//\\n' % (
					example.getValue(rest, './method'),
					example.getValue(rest, './path'))
				modifiers = '//<<static>>// ' if methodIsStatic is True else ''
				methodType = '' if typ is None else ': %s' % typ

				lines.append('%s : + %s%s%s%s' % (classId, restMethodAndPath, modifiers, methodId, methodType))

			if len(methods) > 0:
				lines.append('')

			for relation in sorted(relations, key=lambda rel: rel['id']):
				relationName = example.getValue(relation, './name')
				relationType = example.getValue(relation, './type')
				relationSubType = example.getValue(relation, './subType')

				relationSubTypeIsClass = isinstance(relationSubType, str)
				destination = relationSubType if relationSubTypeIsClass is True else relationType
				stereotype = '//<<%s>>//\\n' % relationType.__name__ if relationSubTypeIsClass is True else ''

				lines.append('%s --> %s : %s%s' % (classId, destination, stereotype, relationName))

		lines.append('@enduml')

		return lines
	#___________________________________________________________________________
	#
	@classmethod
	def generateAnalysis(cls, example, fileradical):

		allLines = []

		scenariosAnalyse = example.findAll(select='.+/analyse\.Scenario::.+/', where='@class .+ analyse\.Scenario')

		for i, scenario in enumerate(scenariosAnalyse.values(), 1):
			id = example.getValue(scenario, './id')
			participants = example.getValue(scenario, './participants')
			interactions = example.getValue(scenario, './interactions')

			svgFile = 'generation.analyse.sequence.%s-%s.svg' % (fileradical, i)
			lines = []

			example.setObject({ '@class' : 'generation.analyse.sequence.diagramme.Plantuml',
					'id'		: id,
					'output'	: svgFile,
					'lines'		: lines,
				})

			lines.append("'%s" % (100 * '_'))
			lines.append("'")
			lines.append('@startuml generation.analyse.sequence.%s-%s.svg' % (fileradical, i))
			lines.append('title "Analyse: %s"' % id)

			cls.manageParticipants(example, participants, lines)
			cls.manageInteractions(example, interactions, lines)

			lines.append('@enduml')

			allLines.extend(lines)

		return allLines
	#___________________________________________________________________________
	#
	@classmethod
	def generateDesign(cls, example, fileradical):

		allLines = []

		scenariosConception = example.findAll(select='.+/conception\.Scenario::.+/', where='@class .+ conception\.Scenario')

		for i, scenario in enumerate(scenariosConception.values(), 1):
			id = example.getValue(scenario, './id')
			participants = dict(example.getValue(scenario, './extend/participants'))
			participants.update(example.getValue(scenario, './participants'))
			interactions = example.getValue(scenario, './extend/interactions')
			addBefores = example.getValue(scenario, './before', default={})
			addAfters = example.getValue(scenario, './after', default={})

			svgFile = 'generation.conception.sequence.%s-%s.svg' % (fileradical, i)
			lines = []

			example.setObject({ '@class' : 'generation.conception.sequence.diagramme.Plantuml',
					'id'		: id,
					'output'	: svgFile,
					'lines'		: lines,
				})

			lines.append("'%s" % (100 * '_'))
			lines.append("'")
			lines.append('@startuml generation.conception.sequence.%s-%s.svg' % (fileradical, i))
			lines.append('title "Conception: %s"' % id)

			cls.manageParticipants(example, participants, lines)
			cls.manageInteractions(example, interactions, lines, addBefores=addBefores, addAfters=addAfters)

			lines.append('@enduml')

			allLines.extend(lines)

		return allLines
	#___________________________________________________________________________
	#
	@classmethod
	def manageParticipants(cls, example, participants, lines):

		lines.append('')

		for participant in participants.values():
			name    = example.getValue(participant, './name')
			label   = example.getValue(participant, './label', default=None)
			classe  = example.getValue(participant, './class', default=None)

			cls.participants[name] = classe

			classe  = classe[ classe.rindex('.') + 1 : ] if classe is not None and '.' in classe else classe
			label   = classe if label is None else label
			typ		= 'actor' if name == 'u' else 'participant'

			lines.append('%s "%s" as %s' % (typ, label, name))
	#___________________________________________________________________________
	#
	@classmethod
	def manageInteractions(cls, example, interactions, lines, addBefores={}, addAfters={}):

		for interaction in interactions:
			type	= example.getValue(interaction, '?/type')
			frm		= example.getValue(interaction, '?/src', default=None)
			to		= example.getValue(interaction, '?/dst', default=None)
			at		= example.getValue(interaction, '?/at', default=None)
			name	= example.getValue(interaction, '?/name', default=None)
			id		= example.getValue(interaction, '?/id', default=None)
			inputs	= example.getValue(interaction, '?/inputs', default={})
			outputs	= example.getValue(interaction, '?/outputs', default={})
			operations = example.getValue(interaction, '?/operations', default=[])

			ios = inputs if type == 'when' else outputs
			arrow = '->' if type == 'when' else '-->'

			addBeforeInteractions = example.getValue(addBefores, '%s/interactions' % id, default=[])
			addBeforeOperations = example.getValue(addBefores, '%s/operations' % id, default=[])

			addAfterInteractions = example.getValue(addAfters, '%s/interactions' % id, default=[])
			addAfterOperations = example.getValue(addAfters, '%s/operations' % id, default=[])

			if at is not None:
				frm = to = at

			if name is None:
				name = ''
			else:
				name = name.replace('§t', '\\t').replace('§n', '\\n')

			if len(addBeforeInteractions) > 0:
				cls.manageInteractions(example, addBeforeInteractions, lines)

			if len(addBeforeOperations) > 0:
				cls.manageExtension(example, addBeforeOperations, lines)

			if type in ('given', 'when'):
				lines.append('')

			if type in ('when', 'then'):
				lines.append('%s %s %s : %s' % (frm, arrow, to, name))

			if len(operations) > 0:
				cls.manageOperations(example, operations, lines)

			if len(ios) > 0:
				lines.append('note over %s' % to)

				for name, id in ios.items():
					lines.append('<#White,#White>| <&media-record> **%s** |: **%s** |' % (name, id))

				lines.append('end note')

			if len(addAfterInteractions) > 0:
				cls.manageInteractions(example, addAfterInteractions, lines)

			if len(addAfterOperations) > 0:
				cls.manageExtension(example, addAfterOperations, lines)
	#___________________________________________________________________________
	#
	@classmethod
	def manageExtension(cls, example, addInteractions, lines):

		cls.currentFrom = 's'

		cls.manageImplementation(example, addInteractions, lines)
	#___________________________________________________________________________
	#
	@classmethod
	def manageImplementation(cls, example, implementation, lines):

		cls.manageOperations(example, implementation, lines)
	#___________________________________________________________________________
	#
	@classmethod
	def manageOperations(cls, example, operations, lines):

		for operation in operations:
			name = example.getValue(operation, '?/name')
			eval('cls.manageOp%s(example, operation, lines)' % name)
	#___________________________________________________________________________
	#
	@classmethod
	def manageOpNew(cls, example, operation, lines):

		participant = example.getValue(operation, '?/participant')
		instance = example.getValue(operation, '?/instance', default=participant)
		parameters = example.getValue(operation, '?/parameters', default={})

		classe = cls.participants[participant]

		constructor = classe[ classe.rindex('.') + 1 : ]
		paramsValues = (',\\n%s' % ('\\t' * max(1, cls.indent))).join([
			'%s=%s' % (
				name,
				str(example.getValue(parameter, './value')
					).replace('}}', ''
					).replace('{{', ''
					)
			)
				for name, parameter in parameters.items() ])
		paramsValues = paramsValues if paramsValues == '' else '\\n%s%s' % ('\\t' * max(1, cls.indent), paramsValues)

		affectation = '%s <&arrow-thick-left> ' % instance if participant == cls.currentFrom and instance != '' else ''

		lines.append('')
		lines.append('%s %s %s : %s' % (cls.currentFrom, '->', participant, '%s%s**<color #blue>//@new//</color>** **%s**(%s)' % (
				cls.TAB * cls.indent, affectation, constructor, paramsValues)))

		if participant != cls.currentFrom:
			lines.append('%s %s %s : %s' % (participant, '-->', cls.currentFrom, instance))
			lines.append('')
	#___________________________________________________________________________
	#
	@classmethod
	def isOperationDefined(cls, example, operation):

		participant = example.getValue(operation, '?/participant')
		methodId = example.getValue(operation, '?/methodId')

		classe = cls.participants[participant]

		return cls.isOperationDefinedFor(example, classe, methodId)
	#___________________________________________________________________________
	#
	@classmethod
	def isOperationDefinedFor(cls, example, classe, methodId):

		methOperations = example.findAll(select='.+/operations/\d+/', where='methodId .+ %s' % example.noRegExp(methodId))
		defines = [ operation for operation in methOperations.values() if example.getValue(operation, '?/name') == 'Define' ]
		nb = 0

		for define in defines:
			implOperations = example.getValue(define, '?/operations', default=[])
			nb = len(implOperations)

		if nb > 0:
			return True

		calls = [ operation for operation in methOperations.values() if example.getValue(operation, '?/name') == 'Call' ]
		nb = 0

		for call in calls:
			implOperations = example.getValue(call, '?/operations', default=[])
			nb += len(implOperations)

		if nb > 0:
			return True

		shortMethodId = methodId[ methodId.rindex('::') +2 : ]

		srcCodeRef = 'input.source.Code::%s' % classe
		srcCodeAccessor = './methods/%s' % shortMethodId

		srcCode = example.getValue(srcCodeRef, srcCodeAccessor, default=None)

		if srcCode is not None:
			return True

		if len(calls) == 0:
			# Si l'opération n'est pas un Call, on ne recherche pas au niveau du parent
			return False

		modelClassRef = 'generation.model.Class::%s' % classe

		modelClass = example.getValue(modelClassRef)
		parentClass = example.getValue(modelClass, './@extends')

		if parentClass is None or parentClass.startswith('.'):
			return False

		parentMethodId = '%s::%s' % (parentClass, shortMethodId)

		return cls.isOperationDefinedFor(example, parentClass, parentMethodId)
	#___________________________________________________________________________
	#
	@classmethod
	def manageOpDefine(cls, example, operation, lines):

		participant = example.getValue(operation, '?/participant')
		instance = example.getValue(operation, '?/instance', default=participant)
		method = example.getValue(operation, '?/method')
		parameters = example.getValue(operation, '?/parameters', default={})
		implOperations = example.getValue(operation, '?/operations', default=[])

		lines.append('== ==')

		if cls.isOperationDefined(example, operation) is False:
			lines.append('note over %s : //**Méthode non implémentée:**//' % cls.currentFrom)

		paramsValues = (',\\n%s' % ('\\t' * max(1, cls.indent))).join([
			'%s=%s' % (
				name,
				str(example.getValue(parameter, './value', default=None)
					).replace('}}', ''
					).replace('{{', ''
					)
			)
				for name, parameter in parameters.items() ])
		paramsValues = paramsValues if paramsValues == '' else '\\n%s%s' % ('\\t' * max(1, cls.indent), paramsValues)

		lines.append('')
		lines.append('%s %s %s : %s' % (cls.currentFrom, '->', participant, '%s**<color #blue>//@def//</color>** **%s**(%s)' % (
				cls.TAB * cls.indent, method, paramsValues)))

		oldFrom = cls.currentFrom
		cls.currentFrom = participant

		if len(implOperations) > 0:
			cls.manageImplementation(example, implOperations, lines)

		cls.currentFrom = oldFrom

		if participant != cls.currentFrom:
			lines.append('%s %s %s : **<color #blue>//@end//</color>** %s' % (participant, '-->', cls.currentFrom, method))
			lines.append('')
	#___________________________________________________________________________
	#
	@classmethod
	def manageOpCall(cls, example, operation, lines):

		returnedVar = example.getValue(operation, '?/returnedVar', default=None)
		participant = example.getValue(operation, '?/participant')
		instance = example.getValue(operation, '?/instance', default=participant)
		method = example.getValue(operation, '?/method')
		parameters = example.getValue(operation, '?/parameters', default={})
		implOperations = example.getValue(operation, '?/operations', default=[])

		if cls.isOperationDefined(example, operation) is False:
			lines.append('note over %s : //**Méthode non implémentée:**//' % cls.currentFrom)

		paramsValues = (',\\n%s' % ('\\t' * max(1, cls.indent))).join([
			'%s=%s' % (
				name,
				str(example.getValue(parameter, './value', default=None)
					).replace('}}', ''
					).replace('{{', ''
					)
			)
				for name, parameter in parameters.items() ])
		paramsValues = paramsValues if paramsValues == '' else '\\n%s%s' % ('\\t' * max(1, cls.indent), paramsValues)

		returnedVar = '' if returnedVar is None else returnedVar
		affectation = '%s <&arrow-thick-left> ' % returnedVar if participant == cls.currentFrom and returnedVar != '' else ''

		lines.append('')
		lines.append('%s %s %s : %s' % (cls.currentFrom, '->', participant, '%s%s**<color #purple>//%s//</color>**.**%s**(%s)' % (
				cls.TAB * cls.indent, affectation, instance, method, paramsValues)))

		oldFrom = cls.currentFrom
		cls.currentFrom = participant

		if len(implOperations) > 0:
			cls.manageImplementation(example, implOperations, lines)

		cls.currentFrom = oldFrom

		if participant != cls.currentFrom:
			lines.append('%s %s %s : %s' % (participant, '-->', cls.currentFrom, returnedVar))
			lines.append('')
	#___________________________________________________________________________
	#
	@classmethod
	def manageOpIf(cls, example, operation, lines):

		condition = example.getValue(operation, '?/condition'
			).replace('}}', ''
			).replace('{{', ''
			)
		condition = re.sub(r'\(\((.*)\)\)', r'**\1**', condition)
		Then = example.getValue(operation, '?/then/operations')
		Else = example.getValue(operation, '?/else/operations', default={})

		lines.append('')
		lines.append('%s %s %s : %s**//<color #blue>@if</color>//** %s' % (cls.currentFrom, '->', cls.currentFrom, cls.TAB * cls.indent, condition))

		if len(Then) > 0:
			cls.indent += 1
			cls.manageImplementation(example, Then, lines)
			cls.indent -= 1

		if len(Else) > 0:
			lines.append('%s %s %s : %s**<color #blue>//@else//</color>**' % (cls.currentFrom, '->', cls.currentFrom, cls.TAB * cls.indent))
			cls.indent += 1
			cls.manageImplementation(example, Else, lines)
			cls.indent -= 1

		lines.append('%s %s %s : %s**<color #blue>//@end if//</color>**' % (cls.currentFrom, '-->', cls.currentFrom, cls.TAB * cls.indent))
		lines.append('')
	#___________________________________________________________________________
	#
	@classmethod
	def manageOpFor(cls, example, operation, lines):

		item = example.getValue(operation, '?/item')
		In = example.getValue(operation, '?/in')
		do = example.getValue(operation, '?/do/operations')

		lines.append('')
		lines.append('%s %s %s : %s**//<color #blue>@for</color>//** %s **//<color #blue>:</color>//** %s' % (
			cls.currentFrom, '->', cls.currentFrom, cls.TAB * cls.indent, item, In))

		if len(do) > 0:
			cls.indent += 1
			cls.manageImplementation(example, do, lines)
			cls.indent -= 1

		lines.append('%s %s %s : %s**<color #blue>//@end for//</color>**' % (cls.currentFrom, '-->', cls.currentFrom, cls.TAB * cls.indent))
		lines.append('')
	#___________________________________________________________________________
	#
	@classmethod
	def manageOpSet(cls, example, operation, lines):

		participant = example.getValue(operation, '?/participant', default=cls.currentFrom)
		var = example.getValue(operation, '?/var')
		value = str(example.getValue(operation, '?/value'
			)).replace('}}', ''
			).replace('{{', ''
			)

		if cls.currentFrom == participant:
			lines.append('%s %s %s : %s%s <&arrow-thick-left> %s' % (cls.currentFrom, '->', cls.currentFrom, cls.TAB * cls.indent, var, value))
		else:
			lines.append('%s %s %s : %s%s' % (cls.currentFrom, '->', participant, cls.TAB * cls.indent, value))
			lines.append('%s %s %s : %s' % (participant, '-->', cls.currentFrom, var))
	#___________________________________________________________________________
	#
	@classmethod
	def manageOpReturn(cls, example, operation, lines):

		value = example.getValue(operation, '?/value'
			).replace('}}', ''
			).replace('{{', ''
			)
		lines.append('%s %s %s : %s**<color #blue>//@return//</color>** %s' % (cls.currentFrom, '->', cls.currentFrom, cls.TAB * cls.indent, value))
		lines.append('')
	#___________________________________________________________________________
	#
	@classmethod
	def manageOpRaise(cls, example, operation, lines):

		exception = example.getValue(operation, '?/exception')
		message = example.getValue(operation, '?/message')
		parameters = example.getValue(operation, '?/parameters')

		paramsValues = '\\n\\t' + ',\\n\\t'.join([
			'%s' % (
				str(parameter
					).replace('}}', ''
					).replace('{{', ''
					)
			)
				for parameter in parameters ])
		paramsValues = '' if paramsValues.strip() == '\\n\\t' else paramsValues
		message = '\\n\\t"' + message + '"' + ('' if len(parameters) == 0 else ',')

		lines.append('%s %s %s : %s**<color #blue>//@raise//</color>** __%s__(%s%s)' % (cls.currentFrom, '->', cls.currentFrom,
				cls.TAB * cls.indent, exception, message, paramsValues))
	#___________________________________________________________________________
	#
	@classmethod
	def manageOpNoop(cls, example, operation, lines):

		# NO-OP
		pass
	#___________________________________________________________________________
	#
	@classmethod
	def manageOpCode(cls, example, operation, lines):

		codeLines = example.getValue(operation, '?/lines')

		lines.append('note over %s : //**Code source**//' % cls.currentFrom)
	#___________________________________________________________________________
	#
	@classmethod
	def generatePlantuml(cls, lines, outputDir, fileradical):

		existsDir = os.path.exists(outputDir)

		if existsDir is True and outputDir.endswith('/output'):
			shutil.rmtree(outputDir)
		os.makedirs(outputDir)

		filename = '%s/%s.puml' % (outputDir, fileradical)
		source = '%s\n' % '\n'.join(lines)

		with open(filename, 'w') as f:
			f.write(source)

		print('>>> [PLANTUML] To SVG: %s' % filename)

		subprocess.run([
				'java',
				'-jar', cls.PLANTUML_JAR,
				'-tsvg', filename
			])
