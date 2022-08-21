@class mvp.View

	@def construire()

		from PyQt5.QtWidgets import *

		layout = QVBoxLayout()
		layout.addWidget(QLabel('IMPLEMENTATION PAR DEFAUT DE LA VUE: %s' % self.titre))
		super().setLayout(layout)

	@def raz()

		pass	# TODO
