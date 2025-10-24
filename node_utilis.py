import config, utils, progress_utils, traceback, log
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow

def insertHeadPressureLeader(*args, **kwargs):
    from ezdxf.enums import TextEntityAlignment
    color=kwargs.get('color')

    try:
        for i in range(0, len(config.df_Junctions)):
            id=config.df_Junctions.at[i,'ID']
            start_x=float(config.df_Junctions.at[i,'x'])
            start_y=float(config.df_Junctions.at[i,'y'])
            result_row=config.df_NodeResults.index[config.df_NodeResults['ID']==str(id)].tolist()[0]
            Head=config.df_NodeResults.at[result_row,'Head']
            Pressure=config.df_NodeResults.at[result_row,'Pressure']

            if (Pressure == None) or (float(Pressure)<0):
                color_pressure=1
            else:
                color_pressure=color

            if (Head == None) or (float(Head)<0):
                color_head=1
            else:
                color_head=color

            leader_up_start_x=start_x+config.text_size
            leader_up_start_y=start_y+config.text_size

            leader_up_end_x=leader_up_start_x+config.leader_distance
            leader_up_end_y=leader_up_start_y+config.leader_distance

            config.msp.add_text(Head, height=config.text_size, dxfattribs={'color': color_head, "style": "epa2HydChart"}).set_placement((leader_up_end_x+6*config.text_size,leader_up_end_y+2*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            config.msp.add_text(Pressure, height=config.text_size, dxfattribs={'color': color_pressure, "style": "epa2HydChart"}).set_placement((leader_up_end_x+6*config.text_size,leader_up_end_y-0.75*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msg= f'節點 {id} 高度及壓力引線已完成繪圖'
            utils.renew_log(msg, False)
            log.setLogToButton()
            progress_utils.setProgress()
    except Exception as e:
        traceback.print_exc()

def insertReservoirsLeader(*args, **kwargs):
    from ezdxf.enums import TextEntityAlignment

    color= kwargs.get('color')
    digits= kwargs.get('digits')

    try:
        for i in range(0, len(config.df_Reservoirs)):
            id=config.df_Reservoirs.at[i,'ID']
            x=float(config.df_Reservoirs.at[i,'x'])
            y=float(config.df_Reservoirs.at[i,'y'])
            head=float(config.df_Reservoirs.at[i,'Head'])
            head=f'{head:.{digits}f}'

            leader_up_start_x=x+config.text_size
            leader_up_start_y=y+config.text_size

            leader_up_end_x=leader_up_start_x+config.leader_distance
            leader_up_end_y=leader_up_start_y+config.leader_distance

            config.msp.add_polyline2d([(leader_up_start_x,leader_up_start_y),
                                (leader_up_end_x,leader_up_end_y),
                                (leader_up_end_x+6*config.text_size,leader_up_end_y)], dxfattribs={'color': color})
            config.msp.add_text(head, height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_up_end_x+6*config.text_size,leader_up_end_y+2*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            config.msp.add_text('ELEV', height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_up_end_x+6*config.text_size,leader_up_end_y+0.75*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            config.msp.add_text('Pressure', height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_up_end_x+6*config.text_size,leader_up_end_y-0.75*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msg=f'接水點 {id} 引線已完成繪圖'
            utils.renew_log(msg, False)
            log.setLogToButton()
            progress_utils.setProgress()
    except Exception as e:
        traceback.print_exc()
