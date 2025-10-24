import globals, utils, progress_utils, traceback
import log
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def insertHeadPressureLeader(*args, **kwargs):
    from ezdxf.enums import TextEntityAlignment
    color=kwargs.get('color')

    try:
        for i in range(0, len(globals.df_Junctions)):
            id=globals.df_Junctions.at[i,'ID']
            start_x=float(globals.df_Junctions.at[i,'x'])
            start_y=float(globals.df_Junctions.at[i,'y'])
            result_row=globals.df_NodeResults.index[globals.df_NodeResults['ID']==str(id)].tolist()[0]
            Head=globals.df_NodeResults.at[result_row,'Head']
            Pressure=globals.df_NodeResults.at[result_row,'Pressure']

            if (Pressure == None) or (float(Pressure)<0):
                color_pressure=1
            else:
                color_pressure=color

            if (Head == None) or (float(Head)<0):
                color_head=1
            else:
                color_head=color

            leader_up_start_x=start_x+globals.text_size
            leader_up_start_y=start_y+globals.text_size

            leader_up_end_x=leader_up_start_x+globals.leader_distance
            leader_up_end_y=leader_up_start_y+globals.leader_distance

            globals.msp.add_text(Head, height=globals.text_size, dxfattribs={'color': color_head, "style": "epa2HydChart"}).set_placement((leader_up_end_x+6*globals.text_size,leader_up_end_y+2*globals.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            globals.msp.add_text(Pressure, height=globals.text_size, dxfattribs={'color': color_pressure, "style": "epa2HydChart"}).set_placement((leader_up_end_x+6*globals.text_size,leader_up_end_y-0.75*globals.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msg= f'節點 {id} 水頭引線已完成繪圖'
            log.renew_log(msg, False)
            log.setLogToButton()
            progress_utils.setProgress(ForcedValue=None)
    except Exception as e:
        traceback.print_exc()

def insertElevAnnotation(*args, **kwargs):
    from ezdxf.enums import TextEntityAlignment

    try:
        color= kwargs.get('color')
        width=kwargs.get('width')

        for i in range(0, len(globals.df_Junctions)):
            id=globals.df_Junctions.at[i,'ID']
            x=float(globals.df_Junctions.at[i,'x'])
            y=float(globals.df_Junctions.at[i,'y'])
            elev=globals.df_Junctions.at[i,'Elev']

            leader_up_start_x=x+globals.text_size
            leader_up_start_y=y+globals.text_size

            leader_up_end_x=leader_up_start_x+globals.leader_distance
            leader_up_end_y=leader_up_start_y+globals.leader_distance

            globals.msp.add_polyline2d([(leader_up_start_x,leader_up_start_y),
                                (leader_up_end_x,leader_up_end_y),
                                (leader_up_end_x+6*globals.text_size,leader_up_end_y)], dxfattribs={'color': color, 'default_start_width': width, 'default_end_width': width})
            globals.msp.add_text(elev, height=globals.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_up_end_x+6*globals.text_size,leader_up_end_y+0.75*globals.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            # msg= f'節點 {id} 高程引線已完成繪圖'
            # log.renew_log(msg, False)
            # log.setLogToButton()
            # progress_utils.setProgress(ForcedValue=None)
    except Exception as e:
        traceback.print_exc()