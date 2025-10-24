import config
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import MainWindow

def setLogToButton(*args, **kwargs):
    config.main_window.MainWindow.browser_log.verticalScrollBar().setValue(config.main_window.MainWindow.browser_log.verticalScrollBar().maximum())
