@class test.OtherTestView

	@def construire()

		from PyQt5.QtWidgets import *

		layout = QVBoxLayout()
		btnConnecter = QPushButton('&Déconnecter')

		layout.addWidget(btnConnecter)

		self.setLayout(layout)

		btnConnecter.clicked.connect(self.onClickDeconnecter)
