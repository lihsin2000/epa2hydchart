import os, traceback
import pandas as pd
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import QCoreApplication
import config
import read_utils
import utils

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def process1(main_window_instance: 'MainWindow'):
    """
    Moved from MainWindow class - processes inp and rpt files to generate DXF output
    """

    try:
        inpFile = config.inpFile
        rptFile = config.rptFile

        digits=main_window_instance.MainWindow.comboBox_digits.currentText()
        config.digit_decimal=digits.count('0')-1

        if inpFile and rptFile:
            dxfPath, _ = QFileDialog.getSaveFileName(main_window_instance, "儲存", "", filter='dxf (*.dxf)')
            file_name = os.path.basename(dxfPath)

            if dxfPath != '':
                (config.df_Coords, config.df_Junctions, config.df_Reservoirs,
                config.df_Tanks, config.df_Pumps, config.df_Valves,
                config.df_Pipes, config.df_Vertices) = utils.inp_to_df(main_window_instance, inpFile, showtime=True)
                if config.hr_list == []:  # 單一時間結果
                    config.df_NodeResults = read_utils.readNodeResults(hr=None, input=config.arranged_rpt_file_path)
                    config.df_LinkResults = read_utils.readLinkResults(hr1=None, input=config.arranged_rpt_file_path)
                    (config.df_NodeResults, config.df_Junctions) = read_utils.changeValueByDigits(digits=config.digit_decimal)
                    matchLink, matchNode = utils.matchInpRptFile()
                    process2(main_window_instance, matchLink=matchLink, matchNode=matchNode, dxfPath=dxfPath, hr='')

                else:   # 多時段結果
                    hr_list_select = []
                    items = main_window_instance.MainWindow.list_hrs.selectedItems()
                    for item in items:
                        hr_list_select.append(item.text())

                    for h in hr_list_select:
                        config.df_NodeResults = read_utils.readNodeResults(hr=h, input=config.arranged_rpt_file_path)
                        i_hr1 = config.hr_list.index(h)
                        i_hr2 = i_hr1 + 1

                        if 1 <= i_hr2 <= len(config.hr_list) - 1:
                            hr2 = config.hr_list[i_hr2]
                            config.df_LinkResults = read_utils.readLinkResults(hr1=h, hr2=hr2, input=config.arranged_rpt_file_path)
                        elif i_hr2 == len(config.hr_list):
                            config.df_LinkResults = read_utils.readLinkResults(hr1=h, hr2='', input=config.arranged_rpt_file_path)

                        matchLink, matchNode = utils.matchInpRptFile()
                        process2(main_window_instance, matchLink=matchLink, matchNode=matchNode, dxfPath=dxfPath, hr=h)


    except Exception as e:
        msg='[Error]不明錯誤，中止匯出'
        utils.renew_log(main_window_instance, msg, True)
        traceback.print_exc()

def process2(main_window_instance: 'MainWindow', *args, **kwargs):
    """
    Moved from MainWindow class - handles DXF generation and file output
    """
    try:
        matchLink = kwargs.get('matchLink')
        matchNode = kwargs.get('matchNode')
        dxfPath = kwargs.get('dxfPath')
        h = kwargs.get('hr')

        if h == '':
            hr_str = ''
        else:
            hr_str = h

        dictionary = os.path.dirname(dxfPath)
        file = os.path.splitext(os.path.basename(dxfPath))[0]

        if matchLink and matchNode:
            msg= f'{hr_str} .rpt及.inp內容相符，開始處理'
            utils.renew_log(main_window_instance, msg, False)
            config.cad, config.msp = main_window_instance.createModelspace()

            tankerLeaderColor = 210
            reservoirLeaderColor = 210
            elevLeaderColor = headPressureLeaderColor = pumpAnnotaionColor = valveAnnotaionColor = 210
            demandColor = 74

            drmandArrowBlock = config.cad.blocks.new(name='demandArrow')
            drmandArrowBlock.add_polyline2d(
                [(0, 0), (0.1, -0.25), (-0.1, -0.25)], close=True, dxfattribs={'color': demandColor})
            drmandArrowBlock.add_hatch(color=demandColor).paths.add_polyline_path(
                [(0, 0), (0.1, -0.25), (-0.1, -0.25)], is_closed=True)

            main_window_instance.createBlocks(config.cad)
            main_window_instance.insertBlocks()
            main_window_instance.pipeLines()
            main_window_instance.pipeAnnotation()
            draw0cmd = main_window_instance.MainWindow.chk_export_0cmd.isChecked()
            
            main_window_instance.demandLeader(color=demandColor, draw0cmd=draw0cmd)
            main_window_instance.elevAnnotation(elevLeaderColor)
            main_window_instance.headPressureLeader(color=headPressureLeaderColor)
            main_window_instance.reservoirsLeader(reservoirLeaderColor)
            main_window_instance.tankLeader(tankerLeaderColor)
            main_window_instance.pumpAnnotation(pumpAnnotaionColor)
            main_window_instance.valveAnnotation(valveAnnotaionColor)
            main_window_instance.addTitle(hr_str=hr_str)

            if dxfPath:
                hr_str = hr_str.replace(':', '-')
                if len(config.hr_list) >= 2:
                    dxfPath = f'{dictionary}/{file}_{hr_str}.dxf'
                dxfPathWithoutExtension = dxfPath.replace('.dxf', '')

                # 檢查dxf是否可以儲存，如果被開啟，則提示用戶重試
                while True:
                    try:
                        config.cad.saveas(dxfPath)
                        break
                    except:
                        traceback.print_exc()
                        from PyQt6.QtWidgets import QApplication, QMessageBox

                        msg_box=QMessageBox(QApplication.activeWindow())
                        msg_box.setIcon(QMessageBox.Icon.Critical)
                        msg_box.setWindowTitle("錯誤")
                        msg_box.setText(f'無法儲存 {dxfPath}，請關閉相關檔案後重試')
                        retry_button = msg_box.addButton("重試", msg_box.ButtonRole.ActionRole)
                        cancel_button = msg_box.addButton("取消", msg_box.ButtonRole.ActionRole)
                        msg_box.exec()
                        if msg_box.clickedButton() == retry_button:
                            continue
                        elif msg_box.clickedButton() == cancel_button:
                            msg=f'[Error]無法儲存 {dxfPath}，中止匯出'
                            utils.renew_log(main_window_instance, msg, True)
                            return

                msg= f'{dxfPathWithoutExtension}.dxf 匯出完成'
                utils.renew_log(main_window_instance, msg, False)
                # QCoreApplication.processEvents()

                svg_path = dxfPath.replace('.dxf', '.svg')
                main_window_instance.save_svg(msp=config.msp, cad=config.cad, path=svg_path)
                msg = f'{dxfPathWithoutExtension}.svg匯出完成'
                utils.renew_log(main_window_instance, msg, False)
                # QCoreApplication.processEvents()

                png_path = dxfPath.replace('.dxf', '.png')
                main_window_instance.convertSVGtoPNG(msp=config.msp, cad=config.cad, pngPath=png_path, svgPath=svg_path)
                msg= f'{dxfPathWithoutExtension}.png匯出完成'
                utils.renew_log(main_window_instance, msg, False)
                # QCoreApplication.processEvents()

                msg= '所有作業成功完成'
                utils.renew_log(main_window_instance, msg, True)

        else:
            msg= f'[Error]{h}.rpt及.inp內容不符，中止匯出'
            utils.renew_log(main_window_instance, msg, True)

    except Exception as e:
        traceback.print_exc()  