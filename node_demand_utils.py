import globals
import progress_utils
import traceback
import log
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def insertDemandLeader(*args, **kwargs):
    try:
        color = kwargs.get('color')
        draw0cmd = kwargs.get('draw0cmd')

        for i in range(0, len(globals.df_Junctions)):
            id = globals.df_Junctions.at[i, 'ID']
            x = float(globals.df_Junctions.at[i, 'x'])
            y = float(globals.df_Junctions.at[i, 'y'])

            l = globals.df_NodeResults.index[globals.df_NodeResults['ID'] == id].tolist()[
                0]
            demand = globals.df_NodeResults.at[l, 'Demand']

            if draw0cmd:
                drawDemandLeader(color=color, id=id, x=x, y=y, demand=demand,
                                 export0cmd=True, width=globals.line_width)
                msg = f'節點 {id} 需水量已完成繪圖'
                log.renewLog(msg, False)
                log.setLogToButton()
                progress_utils.setProgress(ForcedValue=None)
            else:
                drawDemandLeader(color=color, id=id, x=x, y=y, demand=demand,
                                 export0cmd=False, width=globals.line_width)
                msg = f'節點 {id} 需水量已完成繪圖'
                log.renewLog(msg, False)
                log.setLogToButton()
                progress_utils.setProgress(ForcedValue=None)

            QCoreApplication.processEvents()
    except Exception as e:
        traceback.print_exc()


def drawDemandLeader(*args, **kwargs):
    from ezdxf.enums import TextEntityAlignment

    try:
        color = kwargs.get('color')
        id = kwargs.get('id')
        x = kwargs.get('x')
        y = kwargs.get('y')
        demand = kwargs.get('demand')
        export0cmd: bool = kwargs.get('export0cmd')
        width = kwargs.get('width')

        if (export0cmd) or (export0cmd == False and float(demand) != 0.0):
            leader_down_start_x = x+0.5*globals.text_size
            leader_down_start_y = y-0.5*globals.text_size

            leader_down_end_x = leader_down_start_x+globals.leader_distance
            leader_down_end_y = leader_down_start_y-globals.leader_distance

            globals.msp.add_blockref('demandArrow', [leader_down_end_x, leader_down_end_y],
                                     dxfattribs={'xscale': globals.block_size, 'yscale': globals.block_size, 'rotation': 225})
            globals.msp.add_polyline2d([(leader_down_start_x, leader_down_start_y),
                                        (leader_down_end_x, leader_down_end_y)],
                                       dxfattribs={'color': color, 'default_start_width': width, 'default_end_width': width})
            globals.msp.add_text(demand, height=globals.text_size,
                                 dxfattribs={'color': color, "style": "epa2HydChart"})\
                                    .set_placement((leader_down_end_x+0.25*globals.text_size, leader_down_end_y-0.25*globals.text_size), align=TextEntityAlignment.TOP_LEFT)
        elif export0cmd == False and float(demand) == 0.0:
            pass
    except Exception as e:
        traceback.print_exc()
