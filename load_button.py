import globals, utils, log
import os
from PyQt6.QtWidgets import QFileDialog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def handle_inp_file_selection():
    file, type = QFileDialog.getOpenFileName(
        globals.main_window, '開啟inp檔', filter='inp (*.inp)')

    # Only proceed if a file was selected
    if file:
        globals.main_window.MainWindow.l_inp_path.setText(os.path.basename(file))
        globals.inpFile = file
        globals.projName = os.path.splitext(os.path.basename(file))[0]
        globals.main_window.MainWindow.l_projName.setText(globals.projName)
    elif globals.main_window.MainWindow.l_inp_path.text():
        # If no file selected but there's already a path, use the existing one
        file = globals.main_window.MainWindow.l_inp_path.text()
        globals.inpFile = file
        globals.projName = os.path.splitext(os.path.basename(file))[0]
        globals.main_window.MainWindow.l_projName.setText(globals.projName)

def handle_rpt_file_selection():
    file, type = QFileDialog.getOpenFileName(
        globals.main_window, '開啟rpt檔', filter='rpt (*.rpt)')

    # Only proceed if a file was selected or there's an existing path
    if file:
        # Clear existing data and process new file
        globals.main_window.MainWindow.list_hrs.clear()
        globals.main_window.MainWindow.l_rpt_path.setText(os.path.basename(file))

        try:
            globals.arranged_rpt_file_path = utils.arrange_rpt_file(file)
            globals.main_window.MainWindow.browser_log.append('.rpt前處理完成')
            log.set_log_to_button()

            globals.hr_list = utils.convert_patterns_to_hour_list(
                globals.arranged_rpt_file_path)

            if globals.hr_list == []:
                # config.hr_list = ['']
                globals.main_window.MainWindow.list_hrs.addItems(['單一時段'])
                globals.main_window.MainWindow.list_hrs.selectAll()
            else:
                globals.main_window.MainWindow.list_hrs.addItems(globals.hr_list)
                globals.main_window.MainWindow.list_hrs.item(0).setSelected(True)

            globals.rptFile = file

        except Exception as e:
            globals.main_window.MainWindow.browser_log.append(f'[Error] 處理rpt檔時發生錯誤: {str(e)}')
            log.set_log_to_button()

    elif globals.main_window.MainWindow.l_rpt_path.text():
        # If no file selected but there's already a path, use the existing one
        file = globals.main_window.MainWindow.l_rpt_path.text()
        globals.rptFile = file
