import config
import pandas as pd
import re
import traceback
import read_utils
from PyQt6.QtCore import QCoreApplication

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def autoSize(main_window_instance: 'MainWindow'):
    try:
        items = [main_window_instance.MainWindow.l_block_size,
                 main_window_instance.MainWindow.l_joint_size,
                 main_window_instance.MainWindow.l_text_size,
                 main_window_instance.MainWindow.l_leader_distance]

        if main_window_instance.MainWindow.chk_autoSize.isChecked():
            for item in items:
                item.setEnabled(False)
        else:
            for item in items:
                item.setEnabled(True)

        if main_window_instance.MainWindow.chk_autoSize.isChecked() and config.inpFile:
            df_Vertices = read_utils.readVertices(config.inpFile)
            df_Coords = read_utils.readCoords(config.inpFile)
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

            main_window_instance.MainWindow.l_block_size.setText(
                str(blockSizeEstimate))
            main_window_instance.MainWindow.l_joint_size.setText(
                str(blockSizeEstimate/4))
            main_window_instance.MainWindow.l_text_size.setText(
                str(blockSizeEstimate/4))
            main_window_instance.MainWindow.l_leader_distance.setText(
                str(blockSizeEstimate/2))
    except Exception as e:
        traceback.print_exc()


def line2dict(lines, l):
    try:
        text = lines[l].replace('\n', '')
        # text=text.replace('-', ' -')
        text = re.sub(r'\s+', ',', text)
        text = text[:len(text)-1]
        d = text.split(',')
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


def inp_to_df(main_window_instance: 'MainWindow', inpFile, showtime):
    import time
    from PyQt6.QtCore import QCoreApplication
    
    try:  
        t0=time.time()
        config.df_Coords=read_utils.readCoords(inpFile)
        t1=time.time()
        if showtime:
            main_window_instance.MainWindow.browser_log.append(f'節點坐標讀取完畢({t1-t0:.2f}s)')
        QCoreApplication.processEvents()
        config.df_Junctions=read_utils.readJunctions(inpFile)
        t2=time.time()
        if showtime:
            main_window_instance.MainWindow.browser_log.append(f'節點參數讀取完畢({t2-t1:.2f}s)')
        QCoreApplication.processEvents()
        config.df_Reservoirs=read_utils.readReservoirs(inpFile)
        t3=time.time()
        if showtime:
            main_window_instance.MainWindow.browser_log.append(f'接水點參數讀取完畢({t3-t2:.2f}s)')
        QCoreApplication.processEvents()
        config.df_Tanks=read_utils.readTanks(inpFile)
        t4=time.time()
        if showtime:
            main_window_instance.MainWindow.browser_log.append(f'水池參數讀取完畢({t4-t3:.2f}s)')
        QCoreApplication.processEvents()
        config.df_Pumps=read_utils.readPumps(inpFile)
        t5=time.time()
        if showtime:
            main_window_instance.MainWindow.browser_log.append(f'抽水機參數讀取完畢({t5-t4:.2f}s)')
        QCoreApplication.processEvents()
        config.df_Valves=read_utils.readValves(inpFile)
        t6=time.time()
        if showtime:
            main_window_instance.MainWindow.browser_log.append(f'閥件參數讀取完畢({t6-t5:.2f}s)')
        QCoreApplication.processEvents()
        config.df_Pipes=read_utils.readPipes(inpFile)
        t7=time.time()
        if showtime:
            main_window_instance.MainWindow.browser_log.append(f'管件參數讀取完畢({t7-t6:.2f}s)')
        QCoreApplication.processEvents()
        config.df_Vertices=read_utils.readVertices(inpFile)
        t8=time.time()
        if showtime:
            main_window_instance.MainWindow.browser_log.append(f'管件坐標讀取完畢({t8-t7:.2f}s)')
        QCoreApplication.processEvents()
        return (config.df_Coords, config.df_Junctions, config.df_Reservoirs,
                config.df_Tanks, config.df_Pumps, config.df_Valves, config.df_Pipes,
                config.df_Vertices)
    except Exception as e:
        traceback.print_exc()  


def matchInpRptFile():
    try:
        inputAllLink = pd.concat([config.df_Pipes['ID'], config.df_Valves['ID'], config.df_Pumps['ID']])
        inputAllLink = inputAllLink.sort_values().reset_index(drop=True)
        outputAllLink = config.df_LinkResults['ID']
        outputAllLink = outputAllLink.sort_values().reset_index(drop=True)

        matchLink = outputAllLink.equals(outputAllLink)

        inputAllNode = pd.concat([config.df_Junctions['ID'], config.df_Tanks['ID'], config.df_Reservoirs['ID']])
        inputAllNode = inputAllNode.sort_values().reset_index(drop=True)
        outputAllNode = config.df_NodeResults['ID']
        outputAllNode = outputAllNode.sort_values().reset_index(drop=True)

        matchNode = outputAllNode.equals(inputAllNode)
        return matchLink, matchNode
    except Exception as e:
        traceback.print_exc()

def renew_log(main_window_instance: 'MainWindow', msg, seperate:bool):
    """
    Display an error message in the main window's log and set the log to the button.
    """
    
    main_window_instance.MainWindow.browser_log.append(msg)
    if seperate:
        main_window_instance.MainWindow.browser_log.append('---------------------')
    main_window_instance.MainWindow.browser_log.verticalScrollBar().setValue(main_window_instance.MainWindow.browser_log.verticalScrollBar().maximum())
    QCoreApplication.processEvents()
    