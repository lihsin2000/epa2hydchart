import config, utils, log
import os
from PyQt6.QtWidgets import QFileDialog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def loadinpButton():
    file, type = QFileDialog.getOpenFileName(
        config.main_window, '開啟inp檔', filter='inp (*.inp)')

    # Only proceed if a file was selected
    if file:
        config.main_window.MainWindow.l_inp_path.setText(os.path.basename(file))
        config.inpFile = file
        config.projName = os.path.splitext(os.path.basename(file))[0]
        config.main_window.MainWindow.l_projName.setText(config.projName)
    elif config.main_window.MainWindow.l_inp_path.text():
        # If no file selected but there's already a path, use the existing one
        file = config.main_window.MainWindow.l_inp_path.text()
        config.inpFile = file
        config.projName = os.path.splitext(os.path.basename(file))[0]
        config.main_window.MainWindow.l_projName.setText(config.projName)

def loadrptButton():
    file, type = QFileDialog.getOpenFileName(
        config.main_window, '開啟rpt檔', filter='rpt (*.rpt)')

    # Only proceed if a file was selected or there's an existing path
    if file:
        # Clear existing data and process new file
        config.main_window.MainWindow.list_hrs.clear()
        config.main_window.MainWindow.l_rpt_path.setText(os.path.basename(file))

        try:
            config.arranged_rpt_file_path = utils.arrange_rpt_file(file)
            config.main_window.MainWindow.browser_log.append('.rpt前處理完成')
            log.setLogToButton()

            config.hr_list = utils.convertPatternsToHourList(
                config.arranged_rpt_file_path)

            if config.hr_list == []:
                # config.hr_list = ['']
                config.main_window.MainWindow.list_hrs.addItems(['單一時段'])
                config.main_window.MainWindow.list_hrs.selectAll()
            else:
                config.main_window.MainWindow.list_hrs.addItems(config.hr_list)
                config.main_window.MainWindow.list_hrs.item(0).setSelected(True)

            config.rptFile = file

        except Exception as e:
            config.main_window.MainWindow.browser_log.append(f'[Error] 處理rpt檔時發生錯誤: {str(e)}')
            log.setLogToButton()

    elif config.main_window.MainWindow.l_rpt_path.text():
        # If no file selected but there's already a path, use the existing one
        file = config.main_window.MainWindow.l_rpt_path.text()
        config.rptFile = file
