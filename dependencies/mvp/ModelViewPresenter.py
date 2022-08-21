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

		self.useClassPrefix(True)
		#_______________________________________________________________________
		#
		self.setRootPackage('mvp')
		#_______________________________________________________________________
		#
		self.setYamlObject('''
			'@class' : mvp.MainView
			'@extends' : .QMainWindow
			titre : ''
			placeInitiale : ''
			placeInitialeParams : {}
			filArianePlaces : []
			estMaximisee : False
			application :
				'@class' : mvp.Application
				'@extends' : .QApplication
				'@beforeAnyOperation' : True
				'@instantiate' : True
			structures :
				NOM_STRUCTURE :
					'@class' : mvp.StructureView
			services :
				NOM_SERVICE :
					'@class' : mvp.Service
			presenters :
				NOM_PRESENTER :
					'@class' : mvp.Presenter
			places :
				NOM_PLACE :
				-	NOM_PRESENTER_1
				-	NOM_PRESENTER_2
		''')

		self.setYamlObject('''
			'@class' : mvp.StructureView
			'@extends' : .QStackedWidget
		''')

		self.setYamlObject('''
			'@class' : mvp.View
			'@extends' : .QWidget
			titre : ''
###			presenter :
###				'@class' : mvp.Presenter
		''')

		self.setYamlObject('''
			'@class' : mvp.Presenter
			mainView :
				'@class' : mvp.MainView
			services :
				NOM_SERVICE :
					'@class' : mvp.Service
		''')
		#_______________________________________________________________________
		#
		self.setYamlObject('''
			id: MVP - Déclarer les composants
			'@class': analyse.Scenario
			participants:
				s:
					label: Système
			interactions:
			-	when:
					at: s
					name: déclare les composants
					id: declareComponents
		''')
		#_______________________________________________________________________
		#
		self.setYamlObject('''
			id: MVP - Déclarer les composants
			'@class': conception.Scenario
			extend: REF=analyse.Scenario::MVP - Déclarer les composants
			participants:
				mainView:
					class: mvp.MainView
				util:
					class: common.Util
				view:
					class: mvp.View
			after:
				declareComponents:
					operations:
					-	Define:
							participant: mainView
							method: declarerComposants
					-	Define:
							participant: mainView
							method: declarerStructure
							parameters:
								nom:
									type: str
								structureView:
									type: mvp.StructureView
							operations:
							-	Call:
									participant: util
									instance: Util
									method: setEntry
									parameters:
										placeHolder:
											type: dict
											value: this.structures
										entry:
											type: str
											value: nom
										value:
											type: object
											value: structureView
							-	Set:
									participant: mainView
									var: structureView.mainView
									value: this
					-	Define:
							participant: mainView
							method: declarerService
							parameters:
								nom:
									type: str
								service:
									type: mvp.Service
							operations:
							-	Call:
									participant: util
									instance: Util
									method: setEntry
									parameters:
										placeHolder:
											type: dict
											value: this.services
										entry:
											type: str
											value: nom
										value:
											type: object
											value: service
					-	Define:
							participant: mainView
							method: declarerPresenter
							parameters:
								nom:
									type: str
								presenter:
									type: mvp.Presenter
								view:
									type: mvp.View
								nomStructure:
									type: str
								nomsServices:
									type: list
							operations:
							-	Call:
									participant: util
									instance: Util
									method: setEntry
									parameters:
										placeHolder:
											type: dict
											value: this.presenters
										entry:
											type: str
											value: nom
										value:
											type: object
											value: presenter
							-	Set:
									participant: mainView
									var: presenter.mainView
									value: this
							-	Set:
									participant: mainView
									var: presenter.view
									value: view
							-	Set:
									participant: mainView
									var: view.presenter
									value: presenter
							-	Call:
									returnedVar: structure
									participant: util
									instance: Util
									method: getEntry
									parameters:
										placeHolder:
											type: dict
											value: this.structures
										entry:
											type: str
											value: nomStructure
							-	Set:
									participant: mainView
									var: presenter.view.structure
									value: structure
							-	Call:
									participant: view
									method: construire
					-	Define:
							participant: mainView
							method: declarerPlace
							parameters:
								nom:
									type: str
								nomsPresenters:
									type: list
							operations:
							-	Call:
									participant: util
									instance: Util
									method: setEntry
									parameters:
										placeHolder:
											type: dict
											value: this.places
										entry:
											type: str
											value: nom
										value:
											type: object
											value: nomsPresenters
		''')
		#_______________________________________________________________________
		#
		self.setYamlObject('''
			id: "MVP - Lancer l'application"
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
					name: "lance l'application"
					id: launchApp
			-	then:
					src: s
					dst: u
					name: "affiche l'écran de départ"
					id: launchedApp
		''')
		#_______________________________________________________________________
		#
		self.setYamlObject('''
			id: "MVP - Lancer l'application"
			'@class': conception.Scenario
			extend: "REF=analyse.Scenario::MVP - Lancer l'application"
			participants:
				mainView:
					class: mvp.MainView
				presenter:
					class: mvp.Presenter
				view:
					class: mvp.View
				structure:
					class: mvp.StructureView
			after:
				launchApp:
					operations:
					-	Define:
							participant: mainView
							method: executer
							operations:
							-	Call:
									participant: mainView
									instance: this
									method: declarerComposants
									operations:
									-	Noop: {}
							-	Call:
									participant: mainView
									instance: this
									method: installerStructures
									operations:
									-	Noop: {}
							-	Call:
									participant: mainView
									instance: this
									method: allerA
									parameters:
										place:
											type: str
											value: '{{this.placeInitiale}}'
										params:
											type: dict
											value: '{{this.placeInitialeParams}}'
							-	Call:
									participant: mainView
									instance: this
									method: afficher
					-	Define:
							participant: mainView
							method: allerA
							parameters:
								place:
									type: str
								params:
									type: dict
							operations:
							-	For:
									item: nomPresenter
									in: this.places[place]
									do:
									-	Set:
											var: presenter
											type: mvp.Presenter
											value: '{{this.presenters[nomPresenter]}}'
									-	Call:
											participant: presenter
											method: demarrer
											parameters:
												params:
													type: dict
													value: '{{params}}'
											operations:
											-	Call:
													participant: view
													instance: this.view
													method: installer
													operations:
													-	Call:
															participant: structure
															instance: this.structure
															method: setVueCourante
															parameters:
																vue:
																	type: mvp.View
																	value: '{{this}}'
							-	Call:
									participant: mainView
									instance: this
									method: ajouterAuFilAriane
									parameters:
										place:
											type: str
											value: '{{place}}'
		''')
		#
		########################################################################
		#	TEST MVP
		########################################################################
		#
		self.setYamlObject('''
			'@class' : test.TestMainView
			'@extends' : mvp.MainView
			'@finalValues' : True
			titre : Vue principale de test
			placeInitiale : placeTest
			placeInitialeParams : {}
			estMaximisee : True
		''')

		self.setYamlObject('''
			'@class' : test.TestStructureView
			'@extends' : mvp.StructureView
			'@finalValues' : True
		''')

		self.setYamlObject('''
			'@class' : test.TestView
			'@extends' : mvp.View
			'@finalValues' : True
			titre : Vue de test
		''')

		self.setYamlObject('''
			'@class' : test.TestActivity
			'@extends' : mvp.Presenter
			'@finalValues' : True
		''')

		self.setYamlObject('''
			'@class' : test.OtherTestView
			'@extends' : mvp.View
			'@finalValues' : True
			titre : Autre vue de test
		''')

		self.setYamlObject('''
			'@class' : test.OtherTestActivity
			'@extends' : mvp.Presenter
			'@finalValues' : True
		''')
		#_______________________________________________________________________
		#
		self.setYamlObject('''
			id: "Test - MVP"
			'@class': conception.Scenario
			extend: "REF=analyse.Scenario::MVP - Lancer l'application"
			participants:
				mainView:
					class: test.TestMainView
				view:
					class: test.TestView
				presenter:
					class: test.TestActivity
				view1:
					class: test.OtherTestView
				presenter1:
					class: test.OtherTestActivity
				structure:
					class: test.TestStructureView
			after:
				launchApp:
					operations:
					-	New:
							participant: mainView
					-	Call:
							participant: mainView
							method: executer
					-	Define:
							participant: mainView
							method: declarerComposants
							operations:
							-	New:
									instance: testStructureView
									participant: structure
							-	New:
									instance: testView
									participant: view
							-	New:
									instance: testPresenter
									participant: presenter
							-	New:
									instance: otherTestView
									participant: view1
							-	New:
									instance: otherTestPresenter
									participant: presenter1
							-	Call:
									participant: mainView
									instance: super
									method: declarerStructure
									parameters:
										nom:
											type: str
											value: '"structureTest"'
										structureView:
											type: mvp.StructureView
											value: '{{testStructureView}}'
							-	Call:
									participant: mainView
									instance: super
									method: declarerPresenter
									parameters:
										nom:
											type: str
											value: '"presenterTest"'
										presenter:
											type: mvp.Presenter
											value: '{{testPresenter}}'
										view:
											type: mvp.View
											value: '{{testView}}'
										nomStructure:
											type: str
											value: '"structureTest"'
										nomsServices:
											type: list
											value: []
							-	Call:
									participant: mainView
									instance: super
									method: declarerPresenter
									parameters:
										nom:
											type: str
											value: '"otherPresenterTest"'
										presenter:
											type: mvp.Presenter
											value: '{{otherTestPresenter}}'
										view:
											type: mvp.View
											value: '{{otherTestView}}'
										nomStructure:
											type: str
											value: '"structureTest"'
										nomsServices:
											type: list
											value: []
							-	Call:
									participant: mainView
									instance: super
									method: declarerPlace
									parameters:
										nom:
											type: str
											value: '"placeTest"'
										nomsPresenters:
											type: list
											value: [ 'presenterTest' ]
							-	Call:
									participant: mainView
									instance: super
									method: declarerPlace
									parameters:
										nom:
											type: str
											value: '"otherPlaceTest"'
										nomsPresenters:
											type: list
											value: [ 'otherPresenterTest' ]
					-	Define:
							participant: mainView
							method: installerStructures
					-	Define:
							participant: view
							method: construire
					-	Define:
							participant: view1
							method: construire
				launchedApp:
					interactions:
					-	when:
							src: u
							dst: s
							name: 'clique sur "Connecter"'
							operations:
							-	Define:
									participant: view
									instance: this
									method: onClickConnecter
									parameters:
										event:
											type: object
									operations:
									-	Call:
											participant: presenter
											instance: this.presenter
											method: connecter
											operations:
											-	Call:
													participant: mainView
													instance: this.mainView
													method: allerA
													parameters:
														place:
															type: str
															value: '"otherPlaceTest"'
														params:
															type: dict
															value: {}
					-	then:
							src: s
							dst: u
							name: 'affiche le 2ème écran'
					-	when:
							src: u
							dst: s
							name: 'clique sur "Déconnecter"'
							operations:
							-	Define:
									participant: view1
									instance: this
									method: onClickDeconnecter
									parameters:
										event:
											type: object
									operations:
									-	Call:
											participant: presenter1
											instance: this.presenter
											method: deconnecter
											operations:
											-	Call:
													participant: mainView
													instance: this.mainView
													method: allerA
													parameters:
														place:
															type: str
															value: '"placeTest"'
														params:
															type: dict
															value: {}
					-	then:
							src: s
							dst: u
							name: 'retourne vers le 1er écran'
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
