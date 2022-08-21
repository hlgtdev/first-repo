@class mvp.StructureView

	@def setVueCourante(vue: mvp.View)

		vuePrecedente = super().currentWidget()

		if vuePrecedente is not None and vuePrecedente == vue:
			return
		rang = super().indexOf(vue)

		if rang == -1:
			rang = super().addWidget(vue)
		super().setCurrentIndex(rang)
		self.mainView.setWindowTitle('%s - %s' % (self.mainView.titre, vue.titre))

# FIXME: DEL ?
		if vuePrecedente is not None:
			vuePrecedente.raz()
