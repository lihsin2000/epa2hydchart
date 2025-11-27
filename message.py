import globals
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from main import MainWindow


def set_message_to_button():
    """Scroll the log viewer to the bottom."""
    globals.main_window.ui.browser_log.verticalScrollBar().setValue(
        globals.main_window.ui.browser_log.verticalScrollBar().maximum())


def renew_message(msg, seperate: bool):
    """Display a message in the main window's log."""

    globals.main_window.ui.browser_log.append(msg)
    if seperate:
        globals.main_window.ui.browser_log.append('---------------------')
    globals.main_window.ui.browser_log.verticalScrollBar().setValue(
        globals.main_window.ui.browser_log.verticalScrollBar().maximum())
    QCoreApplication.processEvents()
