@class mvp.MainView

	@def ajouterAuFilAriane(place: str)

#		if place != self.getPlaceCourante():
		self.filArianePlaces.append(place)

	@def afficher()

		if self.estMaximisee is True:
			super().showMaximized()
		else:
			super().show()
		self.application.exec_()
