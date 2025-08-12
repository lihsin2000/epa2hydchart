import config, utils
import os
from PyQt6.QtWidgets import QFileDialog
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def loadinpButton(main_window_instance: 'MainWindow'):
    file, type = QFileDialog.getOpenFileName(
        main_window_instance, '開啟inp檔', filter='inp (*.inp)')

    # Only proceed if a file was selected
    if file:
        main_window_instance.MainWindow.l_inp_path.setText(os.path.basename(file))
        config.inpFile = file
        config.projName = os.path.splitext(os.path.basename(file))[0]
        main_window_instance.MainWindow.l_projName.setText(config.projName)
    elif main_window_instance.MainWindow.l_inp_path.text():
        # If no file selected but there's already a path, use the existing one
        file = main_window_instance.MainWindow.l_inp_path.text()
        config.inpFile = file
        config.projName = os.path.splitext(os.path.basename(file))[0]
        main_window_instance.MainWindow.l_projName.setText(config.projName)


def loadrptButton(main_window_instance: 'MainWindow'):
    file, type = QFileDialog.getOpenFileName(
        main_window_instance, '開啟rpt檔', filter='rpt (*.rpt)')

    # Only proceed if a file was selected or there's an existing path
    if file:
        # Clear existing data and process new file
        main_window_instance.MainWindow.list_hrs.clear()
        main_window_instance.MainWindow.l_rpt_path.setText(os.path.basename(file))

        try:
            config.arranged_rpt_file_path = utils.arrange_rpt_file(file)
            main_window_instance.MainWindow.browser_log.append('.rpt前處理完成')
            main_window_instance.setLogToButton()

            config.hr_list = utils.convertPatternsToHourList(
                config.arranged_rpt_file_path)

            if config.hr_list == []:
                # config.hr_list = ['']
                main_window_instance.MainWindow.list_hrs.addItems(['單一時段'])
                main_window_instance.MainWindow.list_hrs.selectAll()
            else:
                main_window_instance.MainWindow.list_hrs.addItems(config.hr_list)
                main_window_instance.MainWindow.list_hrs.item(0).setSelected(True)

            config.rptFile = file

        except Exception as e:
            main_window_instance.MainWindow.browser_log.append(f'[Error] 處理rpt檔時發生錯誤: {str(e)}')
            main_window_instance.setLogToButton()

    elif main_window_instance.MainWindow.l_rpt_path.text():
        # If no file selected but there's already a path, use the existing one
        file = main_window_instance.MainWindow.l_rpt_path.text()
        config.rptFile = file
