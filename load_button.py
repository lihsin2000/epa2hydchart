import globals
import utils
import message
import os
from PyQt6.QtWidgets import QFileDialog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def handle_inp_file_selection():
    """Handle selection of INP input file through file dialog."""
    file, type = QFileDialog.getOpenFileName(
        globals.main_window, '開啟inp檔', filter='inp (*.inp)')

    # Only proceed if a file was selected
    if file:
        globals.main_window.ui.l_inp_path.setText(os.path.basename(file))
        globals.inp_file = file
        globals.proj_name = os.path.splitext(os.path.basename(file))[0]
        globals.main_window.ui.l_projName.setText(globals.proj_name)
    elif globals.main_window.ui.l_inp_path.text():
        # If no file selected but there's already a path, use the existing one
        file = globals.main_window.ui.l_inp_path.text()
        globals.inp_file = file
        globals.proj_name = os.path.splitext(os.path.basename(file))[0]
        globals.main_window.ui.l_projName.setText(globals.proj_name)
    
    # Check if both files are loaded and enable autoSize checkbox
    check_and_enable_autosize()



def handle_rpt_file_selection():
    """Handle selection of RPT report file through file dialog."""
    file, type = QFileDialog.getOpenFileName(
        globals.main_window, '開啟rpt檔', filter='rpt (*.rpt)')

    # Only proceed if a file was selected or there's an existing path
    if file:
        # Clear existing data and process new file
        globals.main_window.ui.list_hrs.clear()
        globals.main_window.ui.l_rpt_path.setText(os.path.basename(file))

        try:
            globals.arranged_rpt_file_path = utils.arrange_rpt_file(file)
            globals.main_window.ui.browser_log.append('.rpt前處理完成')
            message.set_message_to_button()

            globals.hr_list = utils.convert_patterns_to_hour_list(
                globals.arranged_rpt_file_path)

            if globals.hr_list == []:
                # config.hr_list = ['']
                globals.main_window.ui.list_hrs.addItems(['單一時段'])
                globals.main_window.ui.list_hrs.selectAll()
            else:
                globals.main_window.ui.list_hrs.addItems(globals.hr_list)
                globals.main_window.ui.list_hrs.item(0).setSelected(True)

            globals.rpt_file = file

        except Exception as e:
            globals.main_window.ui.browser_log.append(
                f'[Error] 處理rpt檔時發生錯誤: {str(e)}')
            message.set_message_to_button()
            globals.logger.exception(e)

    elif globals.main_window.ui.l_rpt_path.text():
        # If no file selected but there's already a path, use the existing one
        file = globals.main_window.ui.l_rpt_path.text()
        globals.rpt_file = file
    
    # Check if both files are loaded and enable autoSize checkbox
    check_and_enable_autosize()


def check_and_enable_autosize():
    """
    Check if both inp and rpt files are loaded.
    If both are loaded, enable the autoSize checkbox.
    """
    if globals.inp_file and globals.rpt_file:
        globals.main_window.ui.chk_autoSize.setEnabled(True)
    else:
        globals.main_window.ui.chk_autoSize.setEnabled(False)

