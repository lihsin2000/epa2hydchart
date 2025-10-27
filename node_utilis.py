import globals, progress_utils, traceback
import log
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def insert_reservoir_annotation_leader(*args, **kwargs):
    from ezdxf.enums import TextEntityAlignment

    color= kwargs.get('color')
    digits= kwargs.get('digits')

    try:
        for i in range(0, len(globals.df_reservoirs)):
            id=globals.df_reservoirs.at[i,'ID']
            x=float(globals.df_reservoirs.at[i,'x'])
            y=float(globals.df_reservoirs.at[i,'y'])
            head=float(globals.df_reservoirs.at[i,'Head'])
            head=f'{head:.{digits}f}'

            leader_up_start_x=x+globals.text_size
            leader_up_start_y=y+globals.text_size

            leader_up_end_x=leader_up_start_x+globals.leader_distance
            leader_up_end_y=leader_up_start_y+globals.leader_distance

            globals.msp.add_polyline2d([(leader_up_start_x,leader_up_start_y),
                                (leader_up_end_x,leader_up_end_y),
                                (leader_up_end_x+6*globals.text_size,leader_up_end_y)], dxfattribs={'color': color})
            globals.msp.add_text(head, height=globals.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_up_end_x+6*globals.text_size,leader_up_end_y+2*globals.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            globals.msp.add_text('ELEV', height=globals.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_up_end_x+6*globals.text_size,leader_up_end_y+0.75*globals.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            globals.msp.add_text('Pressure', height=globals.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_up_end_x+6*globals.text_size,leader_up_end_y-0.75*globals.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msg=f'接水點 {id} 引線已完成繪圖'
            log.renew_log(msg, False)
            log.set_log_to_button()
            progress_utils.set_progress(forced_value=None)
    except Exception as e:
        traceback.print_exc()

def insert_pump_annotation(*args, **kwargs):
    from ezdxf.enums import TextEntityAlignment
    color=kwargs.get('color')
    digits=kwargs.get('digits')
    try:
        for i in range(0, len(globals.df_pumps)):
            id=globals.df_pumps.at[i,'ID']
            x=float(globals.df_pumps.at[i,'x'])
            y=float(globals.df_pumps.at[i,'y'])

            Q=float(globals.df_pumps.at[i,'Q'])
            H=float(globals.df_pumps.at[i,'H'])

            Q_str=f"{Q:.{digits}f}"
            H_str=f"{H:.{digits}f}"

            offset=[globals.block_size+0.75*globals.text_size,
                    globals.block_size+2*globals.text_size]

            globals.msp.add_text(f'Q:{Q_str}', height=globals.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((x+2*globals.text_size,y-offset[0]), align=TextEntityAlignment.MIDDLE_RIGHT)
            globals.msp.add_text(f'H:{H_str}', height=globals.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((x+2*globals.text_size,y-offset[1]), align=TextEntityAlignment.MIDDLE_RIGHT)
            msg= f'抽水機 {id} 已完成繪圖'
            log.renew_log(msg, False)
            log.set_log_to_button()
            progress_utils.set_progress(forced_value=None)
    except Exception as e:
        traceback.print_exc()

def insert_valve_annotation(color):
    from ezdxf.enums import TextEntityAlignment
    try:
        for i in range(0, len(globals.df_valves)):
            id=globals.df_valves.at[i,'ID']

            x1=float(globals.df_valves.at[i,'Node1_x'])
            y1=float(globals.df_valves.at[i,'Node1_y'])

            x2=float(globals.df_valves.at[i,'Node2_x'])
            y2=float(globals.df_valves.at[i,'Node2_y'])

            x=0.5*(x1+x2)
            y=0.5*(y1+y2)

            Type=globals.df_valves.at[i,'Type']
            Setting=globals.df_valves.at[i,'Setting']

            offset=[globals.block_size+0.75*globals.text_size,
                    globals.block_size+2*globals.text_size]

            globals.msp.add_text(f'{Type}', height=globals.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((x,y-offset[0]), align=TextEntityAlignment.MIDDLE_CENTER)
            globals.msp.add_text(f'{Setting}', height=globals.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((x,y-offset[1]), align=TextEntityAlignment.MIDDLE_CENTER)
            msg= f'閥件 {id} 已完成繪圖'
            log.renew_log(msg, False)
            log.set_log_to_button()
            progress_utils.set_progress(forced_value=None)
    except Exception as e:
        traceback.print_exc()

def insert_tank_annotation_leader(*args, **kwargs):
    from ezdxf.enums import TextEntityAlignment

    color= kwargs.get('color')
    digits= kwargs.get('digits')
    width=kwargs.get('width')
    try:
        for i in range(0, len(globals.df_tanks)):
            id=globals.df_tanks.at[i,'ID']
            x=float(globals.df_tanks.at[i,'x'])
            y=float(globals.df_tanks.at[i,'y'])

            elev=float(globals.df_tanks.at[i,'Elev'])
            elev=f'{elev:.{digits}f}'

            min_elev=float(globals.df_tanks.at[i,'MinElev'])
            min_elev=f'{min_elev:.{digits}f}'

            max_elev=float(globals.df_tanks.at[i,'MaxElev'])
            max_elev=f'{max_elev:.{digits}f}'

            leader_up_start_x=x+globals.text_size
            leader_up_start_y=y+globals.text_size

            leader_up_end_x=leader_up_start_x+globals.leader_distance
            leader_up_end_y=leader_up_start_y+globals.leader_distance

            globals.msp.add_polyline2d([(leader_up_start_x,leader_up_start_y),
                                (leader_up_end_x,leader_up_end_y),
                                (leader_up_end_x+10*globals.text_size,leader_up_end_y)], dxfattribs={'color': 210, 'default_start_width': width, 'default_end_width': width})
            globals.msp.add_text(f'___T', height=globals.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_up_end_x+10*globals.text_size,leader_up_end_y+3.25*globals.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            globals.msp.add_text(f'Hwl:{max_elev}', height=globals.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_up_end_x+10*globals.text_size,leader_up_end_y+2*globals.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            globals.msp.add_text(f'Mwl:{min_elev}', height=globals.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_up_end_x+10*globals.text_size,leader_up_end_y+0.75*globals.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            globals.msp.add_text(f'Elev:{elev}', height=globals.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_up_end_x+10*globals.text_size,leader_up_end_y-0.75*globals.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msg= f'水池 {id} 引線已完成繪圖'
            log.renew_log(msg, False)
            log.set_log_to_button()
            progress_utils.set_progress(forced_value=None)
    except Exception as e:
        traceback.print_exc()
