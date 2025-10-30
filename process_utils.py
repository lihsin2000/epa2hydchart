import os
import traceback
from PyQt6.QtWidgets import QFileDialog
import globals
import read_utils
import utils
import check_utils
import progress_utils
import node_utils
import node_pressure_utils
import pipe_utils
import node_demand_utils
import block_utils
import convert_utils
import message

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def process1():
    """Process inp and rpt files to generate DXF output with hydraulic data."""

    try:
        inp_file = globals.inp_file
        rpt_file = globals.rpt_file

        digits = globals.main_window.ui.comboBox_digits.currentText()
        globals.digit_decimal = digits.count('0')-1

        if inp_file and rpt_file:
            dxf_path, _ = QFileDialog.getSaveFileName(
                globals.main_window, "儲存", "", filter='dxf (*.dxf)')
            file_name = os.path.basename(dxf_path)

            if dxf_path != '':

                utils.load_inp_file_to_dataframe(inp_file, showtime=True)
                globals.output_folder = os.path.dirname(dxf_path)
                check_utils.write_report_header()
                pipe_dimension = check_utils.list_pipe_dimension()
                check_utils.write_report_pipe_dimension(pipe_dimension)

                if globals.hr_list == []:  # 單一時間結果
                    globals.df_node_results = read_utils.read_node_results(
                        None, globals.arranged_rpt_file_path)
                    globals.df_link_results = read_utils.read_link_results(
                        None, '', globals.arranged_rpt_file_path, globals.digit_decimal)
                    progress_utils.set_progress_bar(0)
                    (globals.df_node_results, globals.df_junctions) = read_utils.change_value_by_digits(
                        digits=globals.digit_decimal)
                    match_link, match_node = utils.verify_inp_rpt_files_match()
                    
                    if match_link and match_node:
                        msg = '.rpt及.inp內容相符，開始處理'
                        message.renew_message(msg, False)
                        read_utils.calculate_link_headloss()
                        process2(dxf_path=dxf_path, hr='')

                        headloss_unreasonable_pipes, velocity_unreasonable_pipes = check_utils.find_unreasonable_pipes()
                        low_pressure_junctions, nagaive_pressure = check_utils.find_negative_low_pressure_junctions()

                        check_utils.write_report(headloss_unreasonable_pipes,
                                                 velocity_unreasonable_pipes,
                                                 low_pressure_junctions,
                                                 nagaive_pressure,
                                                 None,
                                                 )
                    else:
                        msg = '[Error].rpt及.inp內容不符，中止匯出'
                        message.renew_message(msg, True)

                else:   # 多時段結果
                    hr_list_select = []
                    items = globals.main_window.ui.list_hrs.selectedItems()
                    for item in items:
                        hr_list_select.append(item.text())

                    for h in hr_list_select:
                        globals.df_node_results = read_utils.read_node_results(
                            h, globals.arranged_rpt_file_path)
                        i_hr1 = globals.hr_list.index(h)
                        i_hr2 = i_hr1 + 1

                        if 1 <= i_hr2 <= len(globals.hr_list) - 1:
                            hr2 = globals.hr_list[i_hr2]
                            globals.df_link_results = read_utils.read_link_results(
                                h, hr2, globals.arranged_rpt_file_path, globals.digit_decimal)
                        elif i_hr2 == len(globals.hr_list):
                            globals.df_link_results = read_utils.read_link_results(
                                h, '', globals.arranged_rpt_file_path, globals.digit_decimal)

                        progress_utils.set_progress_bar(0)

                        match_link, match_node = utils.verify_inp_rpt_files_match()
                        
                        if match_link and match_node:
                            msg = f'{h} .rpt及.inp內容相符，開始處理'
                            message.renew_message(msg, False)
                            read_utils.calculate_link_headloss()
                            process2(dxf_path=dxf_path, hr=h)
                            headloss_unreasonable_pipes, velocity_unreasonable_pipes = check_utils.find_unreasonable_pipes()
                            low_pressure_junctions, nagaive_pressure = check_utils.find_negative_low_pressure_junctions()

                            check_utils.write_report(headloss_unreasonable_pipes,
                                                     velocity_unreasonable_pipes,
                                                     low_pressure_junctions,
                                                     nagaive_pressure,
                                                     h,
                                                     )
                        else:
                            msg = f'[Error]{h}.rpt及.inp內容不符，中止匯出'
                            message.renew_message(msg, True)

    except Exception as e:
        msg = '[Error]不明錯誤，中止匯出'
        message.renew_message(msg, True)
        traceback.print_exc()
        globals.logger.exception(e)


def process2(dxf_path, hr):
    """Generate DXF file with all hydraulic elements and annotations."""

    line_width = globals.line_width

    try:

        if hr == '':
            hr_str = ''
        else:
            hr_str = hr

        dictionary = os.path.dirname(dxf_path)
        file = os.path.splitext(os.path.basename(dxf_path))[0]

        globals.cad, globals.msp = globals.main_window.create_modelspace()

        tanker_leader_color = 210
        reservoir_leader_color = 210
        elev_leader_color = head_pressure_leader_color = pump_annotaion_color = valve_annotaion_color = 210
        demand_color = 74

        drmand_arrow_block = globals.cad.blocks.new(name='demandArrow')
        drmand_arrow_block.add_polyline2d(
            [(0, 0), (0.1, -0.25), (-0.1, -0.25)], close=True, dxfattribs={'color': demand_color})
        drmand_arrow_block.add_hatch(color=demand_color).paths.add_polyline_path(
            [(0, 0), (0.1, -0.25), (-0.1, -0.25)], is_closed=True)

        globals.progress_steps = progress_utils.calculate_progress_steps()
        globals.progress_space = 95 / globals.progress_steps
        globals.progress_value = 0

        block_utils.create_blocks(globals.cad)
        block_utils.insert_blocks(width=line_width)

        pipe_utils.draw_pipe_polylines(width=line_width)
        # Collect pipe annotation boundaries for overlap detection
        pipe_boundaries = pipe_utils.insert_pipe_annotation()

        draw_0cmd = globals.main_window.ui.chk_export_0cmd.isChecked()
        auto_label_post = globals.main_window.ui.chk_autoLabelPost.isChecked()
        node_demand_utils.insert_demand_annotation_leader(
            color=demand_color, draw0cmd=draw_0cmd)
        # Pass pipe boundaries to check for overlaps with node pressure annotations
        node_pressure_utils.insert_pressure_annotation_leader(head_color=head_pressure_leader_color,
                                                              elev_color=elev_leader_color, width=line_width,
                                                              auto_label_post=auto_label_post,
                                                              pipe_boundaries=pipe_boundaries, draw_boundaries=False)
        node_utils.insert_reservoir_annotation_leader(
            color=reservoir_leader_color, digits=globals.digit_decimal)
        node_utils.insert_tank_annotation_leader(
            color=tanker_leader_color, digits=globals.digit_decimal, width=line_width)
        node_utils.insert_pump_annotation(
            color=pump_annotaion_color, digits=globals.digit_decimal)
        node_utils.insert_valve_annotation(valve_annotaion_color)
        utils.add_title(hr_str=hr_str)

        hr_str = hr_str.replace(':', '-')
        if len(globals.hr_list) >= 2:
            dxf_path = f'{dictionary}/{file}_{hr_str}.dxf'
        dxf_path_without_extension = dxf_path.replace('.dxf', '')
        svg_path = dxf_path.replace('.dxf', '.svg')
        png_path = dxf_path.replace('.dxf', '.png')

        if convert_utils.save_dxf(main_window_instance=globals.main_window, dxf_path=dxf_path):
            globals.export_dxf_success = True
            msg = f'{dxf_path_without_extension}.dxf 匯出完成'
        else:
            globals.export_dxf_success = False
            msg = f'[Error]{dxf_path_without_extension}.dxf 匯出失敗'
        message.renew_message(msg, False)
        message.set_message_to_button()
        progress_utils.set_progress_bar(97)

        if convert_utils.save_svg(msp=globals.msp, cad=globals.cad, path=svg_path):
            globals.export_svg_success = True
            msg = f'{dxf_path_without_extension}.svg 匯出完成'
        else:
            globals.export_svg_success = False
            msg = f'[Error]{dxf_path_without_extension}.svg 匯出失敗'
        message.renew_message(msg, False)
        message.set_message_to_button()
        progress_utils.set_progress_bar(98)

        # Synchronous PNG conversion
        if convert_utils.save_png(png_path=png_path, svg_path=svg_path):
            globals.export_png_success = True
            msg = f'{dxf_path_without_extension}.png 匯出完成'
        else:
            globals.export_png_success = False
            msg = f'[Error]{dxf_path_without_extension}.png 匯出失敗'
        message.renew_message(msg, False)
        message.set_message_to_button()
        progress_utils.set_progress_bar(99)

        # Final completion message
        if globals.export_svg_success and globals.export_png_success and globals.export_dxf_success and not globals.any_error:
            final_msg = '所有作業成功完成'
        else:
            final_msg = '作業完成，但有部分錯誤發生，請查看log內容'
        message.renew_message(final_msg, True)
        message.set_message_to_button()
        progress_utils.set_progress_bar(100)


    except Exception as e:
        traceback.print_exc()
        globals.logger.exception(e)
