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
                    config.df_LinkResults = read_utils.readLinkResults(hr1=None, input=config.arranged_rpt_file_path, digits=config.digit_decimal)
                    (config.df_NodeResults, config.df_Junctions) = read_utils.changeValueByDigits(digits=config.digit_decimal)
                    matchLink, matchNode = utils.matchInpRptFile()
                    process2(main_window_instance, matchLink=matchLink, matchNode=matchNode, dxfPath=dxfPath, hr='')
                    headloss_unresonable_pipes=check_pipe_headloss(main_window_instance)
                    pass

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
                            config.df_LinkResults = read_utils.readLinkResults(hr1=h, hr2=hr2, input=config.arranged_rpt_file_path, digits=config.digit_decimal)
                        elif i_hr2 == len(config.hr_list):
                            config.df_LinkResults = read_utils.readLinkResults(hr1=h, hr2='', input=config.arranged_rpt_file_path, digits=config.digit_decimal)

                        matchLink, matchNode = utils.matchInpRptFile()
                        process2(main_window_instance, matchLink=matchLink, matchNode=matchNode, dxfPath=dxfPath, hr=h)


    except Exception as e:
        msg='[Error]不明錯誤，中止匯出'
        utils.renew_log(main_window_instance, msg, True)
        traceback.print_exc()

def check_pipe_headloss(main_window_instance: 'MainWindow', *args, **kwargs):
    link_results= config.df_LinkResults
    pipes=config.df_Pipes
    pumps= config.df_Pumps
    valves= config.df_Valves
    unreasonable_pipes = link_results[abs(link_results['unitHeadloss'].astype(float))>=config.HEADLOSS_THRESHOLD]

    # remove pumps and valves from unreasonable_pipes
    unreasonable_pipes=unreasonable_pipes[~unreasonable_pipes['ID'].isin(pumps['ID'])]
    unreasonable_pipes=unreasonable_pipes[~unreasonable_pipes['ID'].isin(valves['ID'])]

    for index, row in unreasonable_pipes.iterrows():
        pipe_id=row['ID']
        Node1=pipes.loc[pipes['ID']==pipe_id, 'Node1'].values[0]
        Node2=pipes.loc[pipes['ID']==pipe_id, 'Node2'].values[0]
        Diameter=pipes.loc[pipes['ID']==pipe_id, 'Diameter'].values[0]
        unreasonable_pipes.at[index , 'Node1']=Node1
        unreasonable_pipes.at[index , 'Node2']=Node2
        unreasonable_pipes.at[index , 'Diameter']=Diameter
        pass

    return unreasonable_pipes

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
            main_window_instance.insertBlocks(width=config.line_width)
            main_window_instance.pipeLines(width=config.line_width)
            main_window_instance.pipeAnnotation()
            draw0cmd = main_window_instance.MainWindow.chk_export_0cmd.isChecked()
            
            main_window_instance.demandLeader(color=demandColor, draw0cmd=draw0cmd)
            main_window_instance.elevAnnotation(color=elevLeaderColor, width=config.line_width)
            main_window_instance.headPressureLeader(color=headPressureLeaderColor)
            main_window_instance.reservoirsLeader(color=reservoirLeaderColor, digits=config.digit_decimal)
            main_window_instance.tankLeader(color=tankerLeaderColor, digits=config.digit_decimal, width=config.line_width)
            main_window_instance.pumpAnnotation(color=pumpAnnotaionColor, digits=config.digit_decimal)
            main_window_instance.valveAnnotation(valveAnnotaionColor)
            main_window_instance.addTitle(hr_str=hr_str)

            if dxfPath:
                hr_str = hr_str.replace(':', '-')
                if len(config.hr_list) >= 2:
                    dxfPath = f'{dictionary}/{file}_{hr_str}.dxf'
                dxfPathWithoutExtension = dxfPath.replace('.dxf', '')
                svg_path = dxfPath.replace('.dxf', '.svg')
                png_path = dxfPath.replace('.dxf', '.png')
                
                if main_window_instance.save_dxf(main_window_instance=main_window_instance,dxfPath=dxfPath):
                    config.export_dxf_success=True
                    msg= f'{dxfPathWithoutExtension}.dxf 匯出完成'
                else:
                    config.export_dxf_success=False
                    msg= f'[Error]{dxfPathWithoutExtension}.dxf匯出失敗'
                utils.renew_log(main_window_instance, msg, False)


                if main_window_instance.save_svg(msp=config.msp, cad=config.cad, path=svg_path):
                    config.export_svg_success=True
                    msg = f'{dxfPathWithoutExtension}.svg匯出完成'
                else:
                    config.export_svg_success=False
                    msg= f'[Error]{dxfPathWithoutExtension}.svg匯出失敗'
                utils.renew_log(main_window_instance, msg, False)

                if main_window_instance.save_png(pngPath=png_path, svgPath=svg_path):
                    config.export_png_success
                    msg= f'{dxfPathWithoutExtension}.png匯出完成'
                else:
                    config.export_png_success=False
                    msg= f'[Error]{dxfPathWithoutExtension}.png匯出失敗'
                utils.renew_log(main_window_instance, msg, False)


                if config.export_svg_success and config.export_png_success:
                    msg= '所有作業成功完成'
                else:
                    msg= '作業完成，但有部分檔案匯出失敗'
                utils.renew_log(main_window_instance, msg, True)

        else:
            msg= f'[Error]{h}.rpt及.inp內容不符，中止匯出'
            utils.renew_log(main_window_instance, msg, True)

    except Exception as e:
        traceback.print_exc()  