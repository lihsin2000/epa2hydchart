import globals
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import MainWindow

def setLogToButton(*args, **kwargs):
    globals.main_window.MainWindow.browser_log.verticalScrollBar().setValue(globals.main_window.MainWindow.browser_log.verticalScrollBar().maximum())

def renew_log(msg, seperate:bool):
    """
    Display an error message in the main window's log and set the log to the button.
    """

    globals.main_window.MainWindow.browser_log.append(msg)
    if seperate:
        globals.main_window.MainWindow.browser_log.append('---------------------')
    globals.main_window.MainWindow.browser_log.verticalScrollBar().setValue(globals.main_window.MainWindow.browser_log.verticalScrollBar().maximum())
    QCoreApplication.processEvents()
