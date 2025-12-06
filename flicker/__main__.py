from flicker.gui.windows.mainwindow import MainWindow
from flicker.gui.application import FlickerApp

import sys


app = FlickerApp(sys.argv)

window = MainWindow()
window.show()
app.exec()
