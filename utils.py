import globals
import re
import traceback
import read_utils
import log
from PyQt6.QtCore import QCoreApplication

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow
    import pandas as pd


def auto_size():
    """
    Automatically adjust sizing parameters based on input file coordinates.
    """
    import pandas as pd
    try:
        items = [globals.main_window.ui.l_block_size,
                 globals.main_window.ui.l_joint_size,
                 globals.main_window.ui.l_text_size,
                 globals.main_window.ui.l_leader_distance]

        if globals.main_window.ui.chk_autoSize.isChecked():
            for item in items:
                item.setEnabled(False)
        else:
            for item in items:
                item.setEnabled(True)

        if globals.main_window.ui.chk_autoSize.isChecked() and globals.inp_file:
            df_Vertices = read_utils.read_vertices(globals.inp_file)
            df_Coords = read_utils.read_coords(globals.inp_file)
            try:
                coords = df_Coords[['x', 'y']]
            except:
                coords = pd.DataFrame()

            try:
                vertices = df_Vertices[['x', 'y']]
            except:
                vertices = pd.DataFrame()

            min_xs = [float(vertices['x'].min()), float(coords['x'].min())]
            min_xs = [x for x in min_xs if str(x) != 'nan']
            max_xs = [float(vertices['x'].max()), float(coords['x'].max())]
            max_xs = [x for x in max_xs if str(x) != 'nan']

            x_min = min(min_xs)
            x_max = max(max_xs)

            block_size_estimate = float(int((x_max-x_min)/1000)*10)
            if block_size_estimate == 0:
                block_size_estimate = 10

            globals.main_window.ui.l_block_size.setText(
                str(block_size_estimate))
            globals.main_window.ui.l_joint_size.setText(
                str(block_size_estimate/4))
            globals.main_window.ui.l_text_size.setText(
                str(block_size_estimate/4))
            globals.main_window.ui.l_leader_distance.setText(
                str(block_size_estimate/2))
    except Exception as e:
        traceback.print_exc()


def parse_line_to_dictionary(lines, l, position):
    """
    Converts a line of text into a dictionary by splitting it into components.

    Args:
        lines (list): A list of strings, typically read from a file
        l (int): The index of the line to process from the lines list
        position (int): The position in the split line to start processing for special dash handling

    Returns:
        list: A list of values split from the processed line
    """
    try:
        text = lines[l].replace('\n', '')
        text = re.sub(r'\s+', ' ', text)
        d = text.split(' ')
        return d

    except Exception as e:
        traceback.print_exc()


def line_start_end(input, startStr, endStr, start_offset, end_offset):
    """
    Find the start and end line indices containing specific strings.

    Parameters
    ----------
    input : str
        The file path to read.
    startStr : str
        String to find the start line.
    endStr : str
        String to find the end line.
    start_offset : int
        Offset to add to start line index.
    end_offset : int
        Offset to subtract from end line index.

    Returns
    -------
    tuple of int
        (start_line, end_line) indices.
    """
    try:
        index = 0
        with open(input, 'r') as file:
            for line in file:
                index += 1
                if startStr in line:
                    start = index+start_offset
                elif endStr in line:
                    end = index-end_offset
            return start, end
    except Exception as e:
        traceback.print_exc()


def arrange_rpt_file(rptPath):
    """
    Read rpt file, remove unnecessary lines, and write result to temp folder.

    Parameters
    ----------
    rptPath : str
        Path to the RPT file to process.

    Returns
    -------
    str
        Path to the processed file in temp folder.
    """
    import os
    from pathlib import Path
    try:
        if os.path.exists('temp'):
            pass
        else:
            os.mkdir('temp')

        name = Path(rptPath).name
        output = f'temp/{name}'
        if os.path.exists(output):
            os.remove(output)

        with open(rptPath, 'r') as file_in, open(output, 'w') as file_out:
            lines = file_in.readlines()
            i = 0
            while i < len(lines):
                if '\x0c\n' in lines[i]:
                    i += 1
                    continue

                elif 'Page' in lines[i]:
                    i += 1
                    continue

                elif '\n' == lines[i]:
                    i += 1
                    continue

                elif 'continued' in lines[i]:
                    i += 5
                    continue
                else:
                    if i == len(lines)-1:
                        file_out.write('\n')
                        file_out.write('[END]')
                        break
                    else:
                        file_out.write(lines[i])
                        i += 1
        file_out.close()

        return output
    except Exception as e:
        traceback.print_exc()


def convert_patterns_to_hour_list(rptFile2):
    """
    Convert pattern lines from rpt file to a list of unique hour values.

    Parameters
    ----------
    rptFile2 : str
        Path to the RPT file.

    Returns
    -------
    list of str
        List of unique hour values found.
    """
    try:
        rptFile2_lines = open(rptFile2).readlines()

        i = 0
        hr_list = []
        for l in rptFile2_lines:
            if ' Hrs' in l and i == 0:
                h_new = l.split()[3]
                hr_list.append(h_new)
                i += 1
            elif ' Hrs' in l and i > 0:
                h_old = h_new
                h_new = l.split()[3]
                if h_new != h_old:
                    hr_list.append(h_new)
                i += 1

        return hr_list
    except Exception as e:
        traceback.print_exc()


def load_inp_file_to_dataframe(inpFile, showtime):
    """
    Load INP file data into global dataframes and optionally display timing.

    Parameters
    ----------
    inpFile : str
        Path to the INP file.
    showtime : bool
        Whether to display timing messages.
    """
    import time
    from PyQt6.QtCore import QCoreApplication

    try:
        t0 = time.time()
        globals.df_coords = read_utils.read_coords(inpFile)
        t1 = time.time()
        if showtime:
            globals.main_window.ui.browser_log.append(
                f'節點坐標讀取完畢({t1-t0:.2f}s)')
        QCoreApplication.processEvents()
        globals.df_junctions = read_utils.read_junctions(inpFile)
        t2 = time.time()
        if showtime:
            globals.main_window.ui.browser_log.append(
                f'節點參數讀取完畢({t2-t1:.2f}s)')
        QCoreApplication.processEvents()
        globals.df_reservoirs = read_utils.read_reservoirs(inpFile)
        t3 = time.time()
        if showtime:
            globals.main_window.ui.browser_log.append(
                f'接水點參數讀取完畢({t3-t2:.2f}s)')
        QCoreApplication.processEvents()
        globals.df_tanks = read_utils.read_tanks(inpFile)
        t4 = time.time()
        if showtime:
            globals.main_window.ui.browser_log.append(
                f'水池參數讀取完畢({t4-t3:.2f}s)')
        QCoreApplication.processEvents()
        globals.df_pumps = read_utils.read_pumps(inpFile)
        t5 = time.time()
        if showtime:
            globals.main_window.ui.browser_log.append(
                f'抽水機參數讀取完畢({t5-t4:.2f}s)')
        QCoreApplication.processEvents()
        globals.df_valves = read_utils.read_valves(inpFile)
        t6 = time.time()
        if showtime:
            globals.main_window.ui.browser_log.append(
                f'閥件參數讀取完畢({t6-t5:.2f}s)')
        QCoreApplication.processEvents()
        globals.df_pipes = read_utils.read_pipes(inpFile)
        t7 = time.time()
        if showtime:
            globals.main_window.ui.browser_log.append(
                f'管線參數讀取完畢({t7-t6:.2f}s)')
        QCoreApplication.processEvents()
        globals.df_vertices = read_utils.read_vertices(inpFile)
        t8 = time.time()
        if showtime:
            globals.main_window.ui.browser_log.append(
                f'管線坐標讀取完畢({t8-t7:.2f}s)')
        QCoreApplication.processEvents()
        # return (globals.df_coords, globals.df_junctions, globals.df_reservoirs,
        #         globals.df_tanks, globals.df_pumps, globals.df_valves, globals.df_pipes,
        #         globals.df_vertices)
    except Exception as e:
        traceback.print_exc()


def verify_inp_rpt_files_match():
    """
    Verify if the INP and RPT file data match for nodes and links.

    Returns
    -------
    tuple of bool
        (match_links, match_nodes) - True if matches, False otherwise.
    """
    import pandas as pd
    try:
        input_all_link = pd.concat(
            [globals.df_pipes['ID'], globals.df_valves['ID'], globals.df_pumps['ID']])
        input_all_link = input_all_link.sort_values().reset_index(drop=True)
        output_all_link = globals.df_link_results['ID']
        output_all_link = output_all_link.sort_values().reset_index(drop=True)

        match_link = output_all_link.equals(output_all_link)

        input_all_node = pd.concat(
            [globals.df_junctions['ID'], globals.df_tanks['ID'], globals.df_reservoirs['ID']])
        input_all_node = input_all_node.sort_values().reset_index(drop=True)
        output_all_node = globals.df_node_results['ID']
        output_all_node = output_all_node.sort_values().reset_index(drop=True)

        match_node = output_all_node.equals(input_all_node)
        return match_link, match_node
    except Exception as e:
        traceback.print_exc()


def add_title(hr_str):
    """
    Add title text with project name, flow rate, and roughness values to the DXF modelspace.

    Parameters
    ----------
    hr_str : str
        Hour string to include in the title.
    """
    try:
        hr = hr_str

        # 計算左上角座標
        xs = globals.df_coords['x'].tolist()+globals.df_vertices['x'].tolist()
        x_min = min(xs)

        ys = globals.df_coords['y'].tolist()+globals.df_vertices['y'].tolist()
        y_max = max(ys)

        proj_name = globals.main_window.ui.l_projName.text()

        # 計算Q值
        from decimal import Decimal
        Q = 0
        for i in range(0, len(globals.df_junctions)):
            id = globals.df_junctions.at[i, 'ID']
            row = globals.df_node_results.index[globals.df_node_results['ID'] == id].tolist()[
                0]
            if globals.df_node_results.at[row, 'Demand'] != None:
                Q = Q+Decimal(globals.df_node_results.at[row, 'Demand'])
            else:
                msg = f'[Error]節點 {id} Demand數值錯誤，Q值總計可能有誤'
                log.renew_log(msg, False)

        # 匯整C值
        C_str = ''
        Cs = globals.df_pipes['Roughness'].unique()
        for c in Cs:
            C_str = C_str+f'{c},'
        C_str = C_str[:len(C_str)-1]

        # 加入文字
        from ezdxf.enums import TextEntityAlignment
        globals.msp.add_text(proj_name, height=2*globals.text_size, dxfattribs={"style": "epa2HydChart"}).set_placement(
            (x_min, y_max+16*globals.text_size), align=TextEntityAlignment.TOP_LEFT)

        if hr == '':
            globals.msp.add_text(f'Q={Q} CMD', height=2*globals.text_size, dxfattribs={"style": "epa2HydChart"}
                                 ).set_placement((x_min, y_max+13*globals.text_size), align=TextEntityAlignment.TOP_LEFT)
        else:
            globals.msp.add_text(f'{hr} Q={Q} CMD', height=2*globals.text_size, dxfattribs={"style": "epa2HydChart"}
                                 ).set_placement((x_min, y_max+13*globals.text_size), align=TextEntityAlignment.TOP_LEFT)

        globals.msp.add_text(f'C={C_str}', height=2*globals.text_size, dxfattribs={"style": "epa2HydChart"}
                             ).set_placement((x_min, y_max+10*globals.text_size), align=TextEntityAlignment.TOP_LEFT)
    except Exception as e:
        traceback.print_exc()
