import globals
import progress_utils
import traceback
import message
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def insert_reservoir_annotation_leader(color, digits):
    """Insert reservoir annotation leaders with head and elevation information."""
    from ezdxf.enums import TextEntityAlignment
    
    df_reservoirs = globals.df_reservoirs
    msp = globals.msp
    text_size = globals.text_size
    leader_distance = globals.leader_distance

    try:
        for i in range(0, len(df_reservoirs)):
            id = df_reservoirs.at[i, 'ID']
            x = float(df_reservoirs.at[i, 'x'])
            y = float(df_reservoirs.at[i, 'y'])
            head = float(df_reservoirs.at[i, 'Head'])
            head = f'{head:.{digits}f}'

            leader_up_start_x = x+text_size
            leader_up_start_y = y+text_size

            leader_up_end_x = leader_up_start_x+leader_distance
            leader_up_end_y = leader_up_start_y+leader_distance

            msp.add_polyline2d([(leader_up_start_x, leader_up_start_y),
                                        (leader_up_end_x, leader_up_end_y),
                                        (leader_up_end_x+6*text_size, leader_up_end_y)], dxfattribs={'color': color})
            msp.add_text(head, height=text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement(
                (leader_up_end_x+6*text_size, leader_up_end_y+2*text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msp.add_text('ELEV', height=text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement(
                (leader_up_end_x+6*text_size, leader_up_end_y+0.75*text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msp.add_text('Pressure', height=text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement(
                (leader_up_end_x+6*text_size, leader_up_end_y-0.75*text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msg = f'接水點 {id} 引線已完成繪圖'
            message.renew_message(msg, False)
            message.set_message_to_button()
            progress_utils.set_progress_bar(forced_value=None)
    except Exception as e:
        traceback.print_exc()
        globals.logger.exception(e)


def insert_pump_annotation(color, digits):
    """Insert pump annotations showing flow rate and head."""
    from ezdxf.enums import TextEntityAlignment
    
    df_pumps = globals.df_pumps
    msp = globals.msp
    text_size = globals.text_size
    block_size = globals.block_size
    line_width = globals.line_width
    
    try:
        for i in range(0, len(df_pumps)):
            id = df_pumps.at[i, 'ID']
            x = float(df_pumps.at[i, 'x'])
            y = float(df_pumps.at[i, 'y'])

            start = [df_pumps.at[i, 'Node1_x'],
                     df_pumps.at[i, 'Node1_y']]
            end = [df_pumps.at[i, 'Node2_x'],
                   df_pumps.at[i, 'Node2_y']]

            from utils import inerpolate_from_two_points
            try:
                line1_start_x, line1_start_y = inerpolate_from_two_points(
                    x, y, start[0], start[1], 1.5*block_size)
                msp.add_polyline2d([[line1_start_x, line1_start_y], start], dxfattribs={
                                           'default_start_width': line_width, 'default_end_width': line_width})
            
                line2_start_x, line2_start_y = inerpolate_from_two_points(
                    x, y, end[0], end[1], 1.5*block_size)
                msp.add_polyline2d([[line2_start_x, line2_start_y], end], dxfattribs={
                                           'default_start_width': line_width, 'default_end_width': line_width})
            
            except Exception as e:
                traceback.print_exc()
                globals.logger.exception(e)
                
            Q = float(df_pumps.at[i, 'Q'])
            H = float(df_pumps.at[i, 'H'])

            Q_str = f"{Q:.{digits}f}"
            H_str = f"{H:.{digits}f}"

            offset = [block_size+0.75*text_size,
                      block_size+2*text_size]

            msp.add_text(f'Q:{Q_str}', height=text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement(
                (x+2*text_size, y-offset[0]), align=TextEntityAlignment.MIDDLE_RIGHT)
            msp.add_text(f'H:{H_str}', height=text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement(
                (x+2*text_size, y-offset[1]), align=TextEntityAlignment.MIDDLE_RIGHT)
            msg = f'抽水機 {id} 已完成繪圖'
            message.renew_message(msg, False)
            message.set_message_to_button()
            progress_utils.set_progress_bar(forced_value=None)
    except Exception as e:
        traceback.print_exc()
        globals.logger.exception(e)


def insert_valve_annotation(color):
    """Insert valve annotations showing type and setting."""
    from ezdxf.enums import TextEntityAlignment
    
    df_valves = globals.df_valves
    msp = globals.msp
    text_size = globals.text_size
    block_size = globals.block_size

    try:
        for i in range(0, len(df_valves)):
            id = df_valves.at[i, 'ID']

            x1 = float(df_valves.at[i, 'Node1_x'])
            y1 = float(df_valves.at[i, 'Node1_y'])

            x2 = float(df_valves.at[i, 'Node2_x'])
            y2 = float(df_valves.at[i, 'Node2_y'])

            x = 0.5*(x1+x2)
            y = 0.5*(y1+y2)

            Type = df_valves.at[i, 'Type']
            Setting = df_valves.at[i, 'Setting']

            offset = [block_size+0.75*text_size,
                      block_size+2*text_size]

            msp.add_text(f'{Type}', height=text_size, dxfattribs={
                                 'color': color, "style": "epa2HydChart"}).set_placement((x, y-offset[0]), align=TextEntityAlignment.MIDDLE_CENTER)
            msp.add_text(f'{Setting}', height=text_size, dxfattribs={
                                 'color': color, "style": "epa2HydChart"}).set_placement((x, y-offset[1]), align=TextEntityAlignment.MIDDLE_CENTER)
            msg = f'閥件 {id} 已完成繪圖'
            message.renew_message(msg, False)
            message.set_message_to_button()
            progress_utils.set_progress_bar(forced_value=None)
    except Exception as e:
        traceback.print_exc()
        globals.logger.exception(e)


def insert_tank_annotation_leader(color, digits, width):
    """Insert tank annotation leaders with elevation and water level information."""
    from ezdxf.enums import TextEntityAlignment
    
    df_tanks = globals.df_tanks
    msp = globals.msp
    text_size = globals.text_size
    leader_distance = globals.leader_distance

    try:
        for i in range(0, len(df_tanks)):
            id = df_tanks.at[i, 'ID']
            x = float(df_tanks.at[i, 'x'])
            y = float(df_tanks.at[i, 'y'])

            elev = float(df_tanks.at[i, 'Elev'])
            elev = f'{elev:.{digits}f}'

            min_elev = float(df_tanks.at[i, 'MinElev'])
            min_elev = f'{min_elev:.{digits}f}'

            max_elev = float(df_tanks.at[i, 'MaxElev'])
            max_elev = f'{max_elev:.{digits}f}'

            leader_up_start_x = x+text_size
            leader_up_start_y = y+text_size

            leader_up_end_x = leader_up_start_x+leader_distance
            leader_up_end_y = leader_up_start_y+leader_distance

            msp.add_polyline2d([(leader_up_start_x, leader_up_start_y),
                                        (leader_up_end_x, leader_up_end_y),
                                        (leader_up_end_x+10*text_size, leader_up_end_y)], dxfattribs={'color': 210, 'default_start_width': width, 'default_end_width': width})
            msp.add_text(f'___T', height=text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement(
                (leader_up_end_x+10*text_size, leader_up_end_y+3.25*text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msp.add_text(f'Hwl:{max_elev}', height=text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement(
                (leader_up_end_x+10*text_size, leader_up_end_y+2*text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msp.add_text(f'Mwl:{min_elev}', height=text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement(
                (leader_up_end_x+10*text_size, leader_up_end_y+0.75*text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msp.add_text(f'Elev:{elev}', height=text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement(
                (leader_up_end_x+10*text_size, leader_up_end_y-0.75*text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msg = f'水池 {id} 引線已完成繪圖'
            message.renew_message(msg, False)
            message.set_message_to_button()
            progress_utils.set_progress_bar(forced_value=None)
    except Exception as e:
        traceback.print_exc()
        globals.logger.exception(e)
