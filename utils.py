import config
import pandas as pd
import re, traceback
import read_utils

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_pyqt6 import MainWindow

def autoSize(main_window_instance: 'MainWindow'):
    try:
        items=[main_window_instance.MainWindow.l_block_size,
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
            df_Vertices=read_utils.readVertices(config.inpFile)
            df_Coords=read_utils.readCoords(config.inpFile)
            try:
                coords=df_Coords[['x','y']]
            except:
                coords=pd.DataFrame()

            try:
                vertices=df_Vertices[['x','y']]
            except:
                vertices=pd.DataFrame()

            min_xs=[float(vertices['x'].min()),float(coords['x'].min())]
            min_xs=[x for x in min_xs if str(x) != 'nan']
            max_xs=[float(vertices['x'].max()),float(coords['x'].max())]
            max_xs=[x for x in max_xs if str(x) != 'nan']
            
            x_min=min(min_xs)
            x_max=max(max_xs)
            
            blockSizeEstimate=float(int((x_max-x_min)/1000)*10)
            if blockSizeEstimate == 0:
                blockSizeEstimate=10
            
            main_window_instance.MainWindow.l_block_size.setText(str(blockSizeEstimate))
            main_window_instance.MainWindow.l_joint_size.setText(str(blockSizeEstimate/4))
            main_window_instance.MainWindow.l_text_size.setText(str(blockSizeEstimate/4))
            main_window_instance.MainWindow.l_leader_distance.setText(str(blockSizeEstimate/2))
    except Exception as e:
        traceback.print_exc()

def line2dict(lines, l):
    try:
        text=lines[l].replace('\n','')
        # text=text.replace('-', ' -')
        text=re.sub(r'\s+', ',', text)
        text=text[:len(text)-1]
        d=text.split(',')
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
                    start= index+start_offset
                elif endStr in line:
                    end= index-end_offset
            return start, end
    except Exception as e:
        traceback.print_exc()