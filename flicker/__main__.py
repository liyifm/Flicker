from flicker.gui.windows.mainwindow import MainWindow
from flicker.gui.application import FlickerApplication

import sys


app = FlickerApplication(sys.argv)

window = MainWindow()
window.show()
app.exec()
