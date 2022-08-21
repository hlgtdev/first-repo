import os
XMPG_HOME = os.getenv('XMPG_HOME')

import sys
sys.path.append('%s/xmprog/core' % XMPG_HOME)
sys.path.append('%s/xmprog/generator' % XMPG_HOME)

from Example import *
from Generator import *

import yaml
#_______________________________________________________________________________
#
isImported = Example.isImported(__file__)
#_______________________________________________________________________________
#
class Referentiel(Example):

	def define(self):

		self.useClassPrefix(True)
		#_______________________________________________________________________
		#
		self.setValue(ref='entier::a', value=1)
		self.setValue(ref='entier::b', value=2)
		self.setValue(ref='entier::r', value=3)
		#_______________________________________________________________________
		#
		self.setYamlObject('''
			id: Additionner
			'@class': analyse.Scenario
			participants:
				u:
					label: Utilisateur
				s:
					label: Système
			interactions:
			-	when:
					src: u
					dst: s
					name: saisit a et b
					inputs:
						a: REF=entier::a
						b: REF=entier::b
			-	then:
					src: s
					dst: u
			-	when:
					src: u
					dst: s
					name: clique sur +
			-	when:
						at: s
						name: additionne a et b
						id: addAtoB
			-	then:
					src: s
					dst: u
					name: affiche r
					outputs:
						r: REF=entier::r
		''')
		#_______________________________________________________________________
		#
		self.setYamlObject('''
			id: Additionner
			'@class': conception.Scenario
			extend: REF=analyse.Scenario::Additionner
			participants:
				calcEP:
					class: application.endpoint.CalculEndPoint
				calcS:
					class: application.service.CalculService
			after:
				addAtoB:
					operations:
					-	New:
							participant: calcS
							instance: calculService
					-	New:
							participant: calcEP
							instance: calculEndPoint
							parameters:
								calculService:
									type: application.service.CalculService
									value: '{{calculService}}'
					-	Call:
							participant: calcEP
							instance: calculEndPoint
							returnedVar: r
							method: additionner
							parameters:
								a:
									type: int
									value: REF=entier::a
								b:
									type: int
									value: REF=entier::b
							operations:
							-	If:
									condition: 'not [[paramètres valides: {{a}}, {{b}}]]'
									then:
									-	Raise:
											exception: ServiceException
											message: 'Paramètres invalides: a=%s b=%s'
											parameters: [ '{{a}}', '{{b}}' ]
							-	Set:
									var: bUnchanged
									type: int
									value: 0
							-	Set:
									var: bUnchanged
									value: '{{b}} + 1 - 1'
							-	Call:
									participant: calcS
									instance: this.calculService
									returnedVar: r
									method: additionner
									parameters:
										a:
											type: int
											value: '{{a}}'
										b:
											type: int
											value: '{{bUnchanged}} + 0'
									operations:
									-	Return:
											value: '{{a}} + {{b}}'
							-	Return:
									value: '{{r}}'
		''')
	#___________________________________________________________________________
	#
	def process(self):

		if not isImported:
			dryRun = False

			Generator.generate(self, dryRun=dryRun)

			self.showValue(showEmpty=False)
#_______________________________________________________________________________
#
if not isImported:
	Referentiel().run()
