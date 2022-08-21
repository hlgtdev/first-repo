import os
XMPG_HOME = os.getenv('XMPG_HOME')

import sys
sys.path.append('%s/xmprog/core' % XMPG_HOME)
sys.path.append('%s/xmprog/generator' % XMPG_HOME)

from Example import *
from Generator import *
#_______________________________________________________________________________
#
isImported = Example.isImported(__file__)
#_______________________________________________________________________________
#
class Referentiel(Example):

	def define(self):

		self.setRootPackage('xmprog')
		#_______________________________________________________________________
		#
		self.setYamlObject('''
			'@class' : xmprog.generator.AbstractGenerator
		''')

		self.setYamlObject('''
			'@class' : xmprog.generator.ClassGenerator
			'@extends' : application.generator.AbstractGenerator
		''')
		self.setYamlObject('''
			'@class' : xmprog.generator.CodeGenerator
			'@extends' : application.generator.AbstractGenerator
		''')
		self.setYamlObject('''
			'@class' : xmprog.generator.PlantumlGenerator
			'@extends' : application.generator.AbstractGenerator
		''')

		self.setYamlObject('''
			'@class' : xmprog.generator.Generator
		''')
		#_______________________________________________________________________
		#
		self.setYamlObject('''
			id: API
			'@class' : analyse.Scenario
			participants:
				s:
					label: Système
			interactions:
			-	when:
					at: s
					name: "description de l'API: Example"
					id: apiExample
		''')
		#_______________________________________________________________________
		#
		self.setYamlObject('''
				id: API
				'@class': conception.Scenario
				extend: REF=analyse.Scenario::API
				participants:
					xmp:
						class: xmprog.core.Example
				after:
					apiExample:
						operations:
						-	New:
								instance: xmp
								participant: xmp
						-	Call:
								participant: xmp
								method: setRootPackage
								parameters:
									rootPackage:
										type: str
						-	Call:
								participant: xmp
								method: useClassPrefix
								parameters:
									bool:
										type: bool
						-	Call:
								participant: xmp
								method: imports
						-	Call:
								participant: xmp
								method: define
						-	Call:
								participant: xmp
								method: process
						-	Call:
								participant: xmp
								method: run
						-	Call:
								participant: xmp
								method: importExamples
								parameters:
									examples:
										type: list
						-	Call:
								participant: xmp
								method: importProcessors
								parameters:
									examples:
										type: list
						-	Call:
								participant: xmp
								method: newRef
						-	Call:
								participant: xmp
								method: importValues
								parameters:
									examples:
										type: list
						-	Call:
								participant: xmp
								method: debug
								parameters:
									value:
										type: object
									info:
										type: str
						-	Call:
								participant: xmp
								method: showErrorContext
								parameters:
									ref:
										type: object
						-	Call:
								participant: xmp
								method: loadSourceCode
								parameters:
									filename:
										type: str
						-	Call:
								participant: xmp
								method: setObject
								parameters:
									objectAsMap:
										type: dict
									idName:
										type: str
										value: '"id"'
									className:
										type: str
										value: '"@class"'
						-	Call:
								participant: xmp
								method: getValue
								parameters:
									ref:
										type: object
									accessor:
										type: str
									default:
										type: object
									setDefault:
										type: bool
						-	Call:
								participant: xmp
								method: setValue
								parameters:
									ref:
										type: object
									accessor:
										type: str
									value:
										type: object
						-	Call:
								participant: xmp
								method: noRegExp
								parameters:
									s:
										type: str
						-	Call:
								participant: xmp
								method: findAll
								parameters:
									ref:
										type: object
									select:
										type: str
									where:
										type: str
						-	Call:
								participant: xmp
								method: concatAccessors
								parameters:
									accessors:
										type: list
									exists:
										type: bool
						-	Call:
								participant: xmp
								method: showValue
								parameters:
									ref:
										type: object
									accessor:
										type: str
									showEmpty:
										type: bool
									silent:
										type: bool
		''')

	"""
		pathsOpNamedCall = fromExample.getPaths(key, attr='operations', filter='name .* : Call')
		pathAt  = '%s/at' % self.getPathBeforeLast(pathOpNamedCall, '/operations')

		scenarioAccessors = fromExample.findAll(ref=None, select='.', where='@class == "conception.Scenario"')
		operationAccessors = fromExample.findAll(ref=scenario, select='operations/*', where='operations/*/name == "Call"')
		operationAccessors = fromExample.findAll(ref=None, select='operations/*', where=[
				'@class == "conception.Scenario"',
				'operations/*/name == "Call"',
			])

		atAccessors = fromExample.relativeAccess('../at', from=accessor)
		atAccessors = fromExample.relativeAccess('../at', from=[
				operationAccessors
			])

		select
			operations/[]
		from
			Referentiel
		where
			@class = 'conception.Scenario'
			AND operations/**/name = 'Call'
	"""
	#___________________________________________________________________________
	#
	def process(self):

		if not isImported:
			dryRun = False

			Generator.generate(self, dryRun=dryRun)

			self.showRefs()
#_______________________________________________________________________________
#
if not isImported:
	Referentiel()
