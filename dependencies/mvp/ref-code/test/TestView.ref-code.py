@class test.TestView

	@def construire()

		from PyQt5.QtWidgets import *

		layout = QVBoxLayout()
		btnConnecter = QPushButton('&Connecter')

		layout.addWidget(btnConnecter)

		self.setLayout(layout)

		btnConnecter.clicked.connect(self.onClickConnecter)
