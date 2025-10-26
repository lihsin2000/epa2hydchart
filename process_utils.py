import os, traceback
from PyQt6.QtWidgets import QFileDialog
import globals
import read_utils
import utils
import check_utils
import progress_utils
import node_utilis
import node_pressure_utils
import pipe_utils
import node_demand_utils
import block_utils
import convert_utils
import log

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def process1():
    """
    Moved from MainWindow class - processes inp and rpt files to generate DXF output
    """

    try:
        inpFile = globals.inpFile
        rptFile = globals.rptFile

        digits=globals.main_window.MainWindow.comboBox_digits.currentText()
        globals.digit_decimal=digits.count('0')-1

        if inpFile and rptFile:
            dxfPath, _ = QFileDialog.getSaveFileName(globals.main_window, "儲存", "", filter='dxf (*.dxf)')
            file_name = os.path.basename(dxfPath)

            if dxfPath != '':

                utils.inp_to_df(inpFile, showtime=True)
                globals.output_folder=os.path.dirname(dxfPath)
                check_utils.write_report_header()
                pipe_dimension=check_utils.list_pipe_dimension()
                check_utils.write_report_pipe_dimension(pipe_dimension=pipe_dimension)
                
                if globals.hr_list == []:  # 單一時間結果
                    globals.df_NodeResults = read_utils.readNodeResults(hr=None, input=globals.arranged_rpt_file_path)
                    globals.df_LinkResults = read_utils.readLinkResults(hr1=None, input=globals.arranged_rpt_file_path, digits=globals.digit_decimal)
                    progress_utils.setProgress(0)
                    (globals.df_NodeResults, globals.df_Junctions) = read_utils.changeValueByDigits(digits=globals.digit_decimal)
                    matchLink, matchNode = utils.IsInpRptMatch()
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
                    items = globals.main_window.MainWindow.list_hrs.selectedItems()
                    for item in items:
                        hr_list_select.append(item.text())

                    for h in hr_list_select:
                        globals.df_NodeResults = read_utils.readNodeResults(hr=h, input=globals.arranged_rpt_file_path)
                        i_hr1 = globals.hr_list.index(h)
                        i_hr2 = i_hr1 + 1

                        if 1 <= i_hr2 <= len(globals.hr_list) - 1:
                            hr2 = globals.hr_list[i_hr2]
                            globals.df_LinkResults = read_utils.readLinkResults(hr1=h, hr2=hr2, input=globals.arranged_rpt_file_path, digits=globals.digit_decimal)
                        elif i_hr2 == len(globals.hr_list):
                            globals.df_LinkResults = read_utils.readLinkResults(hr1=h, hr2='', input=globals.arranged_rpt_file_path, digits=globals.digit_decimal)

                        progress_utils.setProgress(0)
                        
                        matchLink, matchNode = utils.IsInpRptMatch()
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
        log.renewLog(msg, True)
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
            log.renewLog(msg, False)
            globals.cad, globals.msp = globals.main_window.createModelspace()

            tankerLeaderColor = 210
            reservoirLeaderColor = 210
            elevLeaderColor = headPressureLeaderColor = pumpAnnotaionColor = valveAnnotaionColor = 210
            demandColor = 74

            drmandArrowBlock = globals.cad.blocks.new(name='demandArrow')
            drmandArrowBlock.add_polyline2d(
                [(0, 0), (0.1, -0.25), (-0.1, -0.25)], close=True, dxfattribs={'color': demandColor})
            drmandArrowBlock.add_hatch(color=demandColor).paths.add_polyline_path(
                [(0, 0), (0.1, -0.25), (-0.1, -0.25)], is_closed=True)

            globals.progress_steps = progress_utils.calculateProgressSteps()
            globals.progress_space= 95 / globals.progress_steps
            globals.progress_value=0
            
            block_utils.createBlocks(globals.cad)
            block_utils.insertBlocks(width=globals.line_width)

            pipe_utils.insertPipeLines(width=globals.line_width)
            # Collect pipe annotation boundaries for overlap detection
            pipe_boundaries = pipe_utils.insertPipeAnnotation()
            
            draw0cmd = globals.main_window.MainWindow.chk_export_0cmd.isChecked()
            autoLabelPost = globals.main_window.MainWindow.chk_autoLabelPost.isChecked()
            node_demand_utils.insertDemandLeader(color=demandColor, draw0cmd=draw0cmd)
            # Pass pipe boundaries to check for overlaps with node pressure annotations
            node_pressure_utils.insertHeadPressureLeader(HeadColor=headPressureLeaderColor, 
                                                        ElevColor=elevLeaderColor, width=globals.line_width,
                                                        autoLabelPost=autoLabelPost,
                                                        pipe_boundaries=pipe_boundaries)
            node_utilis.insertReservoirsLeader(color=reservoirLeaderColor, digits=globals.digit_decimal)
            node_utilis.insertTankLeader(color=tankerLeaderColor, digits=globals.digit_decimal, width=globals.line_width)
            node_utilis.insertPumpAnnotation(color=pumpAnnotaionColor, digits=globals.digit_decimal)
            node_utilis.insertValveAnnotation(valveAnnotaionColor)
            utils.addTitle(hr_str=hr_str)

            hr_str = hr_str.replace(':', '-')
            if len(globals.hr_list) >= 2:
                dxfPath = f'{dictionary}/{file}_{hr_str}.dxf'
            dxfPathWithoutExtension = dxfPath.replace('.dxf', '')
            svg_path = dxfPath.replace('.dxf', '.svg')
            png_path = dxfPath.replace('.dxf', '.png')
            
            if convert_utils.save_dxf(main_window_instance=globals.main_window, dxfPath=dxfPath):
                globals.export_dxf_success=True
                msg= f'{dxfPathWithoutExtension}.dxf 匯出完成'
            else:
                globals.export_dxf_success=False
                msg= f'[Error]{dxfPathWithoutExtension}.dxf 匯出失敗'
            log.renewLog(msg, False)
            log.setLogToButton()
            progress_utils.setProgress(97)

            if convert_utils.save_svg(msp=globals.msp, cad=globals.cad, path=svg_path):
                globals.export_svg_success=True
                msg = f'{dxfPathWithoutExtension}.svg 匯出完成'
            else:
                globals.export_svg_success=False
                msg= f'[Error]{dxfPathWithoutExtension}.svg 匯出失敗'
            log.renewLog(msg, False)
            log.setLogToButton()
            progress_utils.setProgress(98)

            # PNG conversion callback to handle async completion
            def on_png_complete(success):
                if success:
                    globals.export_png_success = True
                    msg = f'{dxfPathWithoutExtension}.png 匯出完成'
                else:
                    globals.export_png_success = False
                    msg = f'[Error]{dxfPathWithoutExtension}.png 匯出失敗'
                log.renewLog(msg, False)
                log.setLogToButton()
                progress_utils.setProgress(99)
                
                # Final completion message
                if globals.export_svg_success and globals.export_png_success and globals.export_dxf_success and not globals.any_error:
                    final_msg = '所有作業成功完成'
                else:
                    final_msg = '作業完成，但有部分錯誤發生，請查看log內容'
                log.renewLog(final_msg, True)
                log.setLogToButton()
                progress_utils.setProgress(100)
            
            # Start async PNG conversion with callback
            convert_utils.save_png(pngPath=png_path, svgPath=svg_path, callback=on_png_complete)

        else:
            msg= f'[Error]{h}.rpt及.inp內容不符，中止匯出'
            log.renewLog(msg, True)

    except Exception as e:
        traceback.print_exc()
