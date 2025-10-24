import os, traceback
import pandas as pd
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import QCoreApplication
import config
import read_utils
import utils
import check_utils
import progress_utils
import node_utilis

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def process1():
    """
    Moved from MainWindow class - processes inp and rpt files to generate DXF output
    """

    try:
        inpFile = config.inpFile
        rptFile = config.rptFile

        digits=config.main_window.MainWindow.comboBox_digits.currentText()
        config.digit_decimal=digits.count('0')-1

        if inpFile and rptFile:
            dxfPath, _ = QFileDialog.getSaveFileName(config.main_window, "儲存", "", filter='dxf (*.dxf)')
            file_name = os.path.basename(dxfPath)

            if dxfPath != '':
                (config.df_Coords, config.df_Junctions, config.df_Reservoirs,
                config.df_Tanks, config.df_Pumps, config.df_Valves,
                config.df_Pipes, config.df_Vertices) = utils.inp_to_df(inpFile, showtime=True)
                
                config.output_folder=os.path.dirname(dxfPath)

                check_utils.write_report_header()
                pipe_dimension=check_utils.list_pipe_dimension()
                check_utils.write_report_pipe_dimension(pipe_dimension=pipe_dimension)
                
                if config.hr_list == []:  # 單一時間結果
                    config.df_NodeResults = read_utils.readNodeResults(hr=None, input=config.arranged_rpt_file_path)
                    config.df_LinkResults = read_utils.readLinkResults(hr1=None, input=config.arranged_rpt_file_path, digits=config.digit_decimal)
                    (config.df_NodeResults, config.df_Junctions) = read_utils.changeValueByDigits(digits=config.digit_decimal)
                    matchLink, matchNode = utils.matchInpRptFile()
                    process2(matchLink=matchLink, matchNode=matchNode, dxfPath=dxfPath, hr='')
                    
                    headloss_unreasonable_pipes, velocity_unreasonable_pipes=check_utils.filter_unreasonable_pipes()
                    low_pressure_junctions, nagavite_pressure=check_utils.check_negative_low_pressure_junctions()

                    check_utils.write_report(headloss_unreasonable_pipes,
                                             velocity_unreasonable_pipes,
                                             low_pressure_junctions,
                                             nagavite_pressure,
                                             None,
                                             )
                    # pass

                else:   # 多時段結果
                    hr_list_select = []
                    items = config.main_window.MainWindow.list_hrs.selectedItems()
                    for item in items:
                        hr_list_select.append(item.text())

                    for h in hr_list_select:
                        config.df_NodeResults = read_utils.readNodeResults(hr=h, input=config.arranged_rpt_file_path)
                        i_hr1 = config.hr_list.index(h)
                        i_hr2 = i_hr1 + 1

                        if 1 <= i_hr2 <= len(config.hr_list) - 1:
                            hr2 = config.hr_list[i_hr2]
                            config.df_LinkResults = read_utils.readLinkResults(hr1=h, hr2=hr2, input=config.arranged_rpt_file_path, digits=config.digit_decimal)
                        elif i_hr2 == len(config.hr_list):
                            config.df_LinkResults = read_utils.readLinkResults(hr1=h, hr2='', input=config.arranged_rpt_file_path, digits=config.digit_decimal)

                        matchLink, matchNode = utils.matchInpRptFile()
                        process2(matchLink=matchLink, matchNode=matchNode, dxfPath=dxfPath, hr=h)
                        headloss_unreasonable_pipes, velocity_unreasonable_pipes=check_utils.filter_unreasonable_pipes()
                        low_pressure_junctions, nagavite_pressure=check_utils.check_negative_low_pressure_junctions()
                        
                    check_utils.write_report(headloss_unreasonable_pipes,
                                             velocity_unreasonable_pipes,
                                             low_pressure_junctions,
                                             nagavite_pressure,
                                             h,
                                             )

    except Exception as e:
        msg='[Error]不明錯誤，中止匯出'
        utils.renew_log(msg, True)
        traceback.print_exc()

def process2(*args, **kwargs):
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
            utils.renew_log(msg, False)
            config.cad, config.msp = config.main_window.createModelspace()

            tankerLeaderColor = 210
            reservoirLeaderColor = 210
            elevLeaderColor = headPressureLeaderColor = pumpAnnotaionColor = valveAnnotaionColor = 210
            demandColor = 74

            drmandArrowBlock = config.cad.blocks.new(name='demandArrow')
            drmandArrowBlock.add_polyline2d(
                [(0, 0), (0.1, -0.25), (-0.1, -0.25)], close=True, dxfattribs={'color': demandColor})
            drmandArrowBlock.add_hatch(color=demandColor).paths.add_polyline_path(
                [(0, 0), (0.1, -0.25), (-0.1, -0.25)], is_closed=True)

            config.progress_steps = progress_utils.calculateProgressSteps()
            config.progress_space= 100 / config.progress_steps
            config.progress_value=0

            config.main_window.createBlocks(config.cad)
            config.main_window.insertBlocks(width=config.line_width)
            config.main_window.insertPipeLines(width=config.line_width)
            config.main_window.insertPipeAnnotation()
            
            draw0cmd = config.main_window.MainWindow.chk_export_0cmd.isChecked()
            config.main_window.insertDemandLeader(color=demandColor, draw0cmd=draw0cmd)
            config.main_window.insertElevAnnotation(color=elevLeaderColor, width=config.line_width)
            node_utilis.insertHeadPressureLeader(color=headPressureLeaderColor)
            node_utilis.insertReservoirsLeader(color=reservoirLeaderColor, digits=config.digit_decimal)
            config.main_window.insertTankLeader(color=tankerLeaderColor, digits=config.digit_decimal, width=config.line_width)
            config.main_window.insertPumpAnnotation(color=pumpAnnotaionColor, digits=config.digit_decimal)
            config.main_window.insertValveAnnotation(valveAnnotaionColor)
            config.main_window.addTitle(hr_str=hr_str)

            hr_str = hr_str.replace(':', '-')
            if len(config.hr_list) >= 2:
                dxfPath = f'{dictionary}/{file}_{hr_str}.dxf'
            dxfPathWithoutExtension = dxfPath.replace('.dxf', '')
            svg_path = dxfPath.replace('.dxf', '.svg')
            png_path = dxfPath.replace('.dxf', '.png')
            
            if config.main_window.save_dxf(main_window_instance=config.main_window, dxfPath=dxfPath):
                config.export_dxf_success=True
                msg= f'{dxfPathWithoutExtension}.dxf 匯出完成'
            else:
                config.export_dxf_success=False
                msg= f'[Error]{dxfPathWithoutExtension}.dxf匯出失敗'
            utils.renew_log(msg, False)

            if config.main_window.save_svg(msp=config.msp, cad=config.cad, path=svg_path):
                config.export_svg_success=True
                msg = f'{dxfPathWithoutExtension}.svg匯出完成'
            else:
                config.export_svg_success=False
                msg= f'[Error]{dxfPathWithoutExtension}.svg匯出失敗'
            utils.renew_log(msg, False)

            if config.main_window.save_png(pngPath=png_path, svgPath=svg_path):
                config.export_png_success=True
                msg= f'{dxfPathWithoutExtension}.png匯出完成'
            else:
                config.export_png_success=False
                msg= f'[Error]{dxfPathWithoutExtension}.png匯出失敗'
            utils.renew_log(msg, False)

            if config.export_svg_success and config.export_png_success and config.export_dxf_success and not config.any_error:
                msg= '所有作業成功完成'
            else:
                msg= '作業完成，但有部分錯誤發生，請查看log內容'
            utils.renew_log(msg, True)

        else:
            msg= f'[Error]{h}.rpt及.inp內容不符，中止匯出'
            utils.renew_log(msg, True)

    except Exception as e:
        traceback.print_exc()
