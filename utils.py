import globals
import pandas as pd
import re
import traceback
import read_utils
import progress_utils
from PyQt6.QtCore import QCoreApplication

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def autoSize():
    try:
        items = [globals.main_window.MainWindow.l_block_size,
                 globals.main_window.MainWindow.l_joint_size,
                 globals.main_window.MainWindow.l_text_size,
                 globals.main_window.MainWindow.l_leader_distance]

        if globals.main_window.MainWindow.chk_autoSize.isChecked():
            for item in items:
                item.setEnabled(False)
        else:
            for item in items:
                item.setEnabled(True)

        if globals.main_window.MainWindow.chk_autoSize.isChecked() and globals.inpFile:
            df_Vertices = read_utils.readVertices(globals.inpFile)
            df_Coords = read_utils.readCoords(globals.inpFile)
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

            blockSizeEstimate = float(int((x_max-x_min)/1000)*10)
            if blockSizeEstimate == 0:
                blockSizeEstimate = 10

            globals.main_window.MainWindow.l_block_size.setText(
                str(blockSizeEstimate))
            globals.main_window.MainWindow.l_joint_size.setText(
                str(blockSizeEstimate/4))
            globals.main_window.MainWindow.l_text_size.setText(
                str(blockSizeEstimate/4))
            globals.main_window.MainWindow.l_leader_distance.setText(
                str(blockSizeEstimate/2))
    except Exception as e:
        traceback.print_exc()

# def line2dict(lines, l, position):
#     """
#     Converts a line of text into a dictionary by splitting it into components.

#     Args:
#         lines (list): A list of strings, typically read from a file
#         l (int): The index of the line to process from the lines list
#         position (int): The position in the split line to start processing for special dash handling

#     Returns:
#         list: A list of values split from the processed line
#     """
#     try:
#         dash_in_string=False
#         text = lines[l].replace('\n', '')
#         # text=text.replace('-', ' -')
#         text = re.sub(r'\s+', ',', text)
#         # text = text[:len(text)-1]
#         d = text.split(',')
#         for i in range(position,len(d)):
#             item=d[i]
#             position_for_dash=item.find('-')
#             if '-' in item and position_for_dash != 0:
#                 dash_in_string=True
#                 break

#         if dash_in_string:
#             text_after_position=','.join(d[position:])
#             text_after_position=text_after_position.replace('-', ',-')
#             text_new=','.join(d[0:position])+','+text_after_position
#             d = text_new.split(',')
#             return d
#         else:
#             return d
#     except Exception as e:
#         traceback.print_exc()

def line2dict(lines, l, position):
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

def lineStartEnd(input, startStr, endStr, start_offset, end_offset):
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
    讀取rpt檔，移除不必要的行，並將結果寫入temp資料夾內。
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


def convertPatternsToHourList(rptFile2):
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


def inp_to_df(inpFile, showtime):
    import time
    from PyQt6.QtCore import QCoreApplication

    try:
        t0=time.time()
        globals.df_Coords=read_utils.readCoords(inpFile)
        t1=time.time()
        if showtime:
            globals.main_window.MainWindow.browser_log.append(f'節點坐標讀取完畢({t1-t0:.2f}s)')
        QCoreApplication.processEvents()
        globals.df_Junctions=read_utils.readJunctions(inpFile)
        t2=time.time()
        if showtime:
            globals.main_window.MainWindow.browser_log.append(f'節點參數讀取完畢({t2-t1:.2f}s)')
        QCoreApplication.processEvents()
        globals.df_Reservoirs=read_utils.readReservoirs(inpFile)
        t3=time.time()
        if showtime:
            globals.main_window.MainWindow.browser_log.append(f'接水點參數讀取完畢({t3-t2:.2f}s)')
        QCoreApplication.processEvents()
        globals.df_Tanks=read_utils.readTanks(inpFile)
        t4=time.time()
        if showtime:
            globals.main_window.MainWindow.browser_log.append(f'水池參數讀取完畢({t4-t3:.2f}s)')
        QCoreApplication.processEvents()
        globals.df_Pumps=read_utils.readPumps(inpFile)
        t5=time.time()
        if showtime:
            globals.main_window.MainWindow.browser_log.append(f'抽水機參數讀取完畢({t5-t4:.2f}s)')
        QCoreApplication.processEvents()
        globals.df_Valves=read_utils.readValves(inpFile)
        t6=time.time()
        if showtime:
            globals.main_window.MainWindow.browser_log.append(f'閥件參數讀取完畢({t6-t5:.2f}s)')
        QCoreApplication.processEvents()
        globals.df_Pipes=read_utils.readPipes(inpFile)
        t7=time.time()
        if showtime:
            globals.main_window.MainWindow.browser_log.append(f'管件參數讀取完畢({t7-t6:.2f}s)')
        QCoreApplication.processEvents()
        globals.df_Vertices=read_utils.readVertices(inpFile)
        t8=time.time()
        if showtime:
            globals.main_window.MainWindow.browser_log.append(f'管件坐標讀取完畢({t8-t7:.2f}s)')
        QCoreApplication.processEvents()
        return (globals.df_Coords, globals.df_Junctions, globals.df_Reservoirs,
                globals.df_Tanks, globals.df_Pumps, globals.df_Valves, globals.df_Pipes,
                globals.df_Vertices)
    except Exception as e:
        traceback.print_exc()


def matchInpRptFile():
    try:
        inputAllLink = pd.concat([globals.df_Pipes['ID'], globals.df_Valves['ID'], globals.df_Pumps['ID']])
        inputAllLink = inputAllLink.sort_values().reset_index(drop=True)
        outputAllLink = globals.df_LinkResults['ID']
        outputAllLink = outputAllLink.sort_values().reset_index(drop=True)

        matchLink = outputAllLink.equals(outputAllLink)

        inputAllNode = pd.concat([globals.df_Junctions['ID'], globals.df_Tanks['ID'], globals.df_Reservoirs['ID']])
        inputAllNode = inputAllNode.sort_values().reset_index(drop=True)
        outputAllNode = globals.df_NodeResults['ID']
        outputAllNode = outputAllNode.sort_values().reset_index(drop=True)

        matchNode = outputAllNode.equals(inputAllNode)
        return matchLink, matchNode
    except Exception as e:
        traceback.print_exc()
