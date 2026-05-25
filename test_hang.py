import sys
from PyQt6.QtWidgets import QApplication
from pyqt_app.views.auth_view import AuthView
app = QApplication(sys.argv)
v = AuthView()
v.show()
QApplication.processEvents()
print("Success!")
