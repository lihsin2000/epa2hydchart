import globals
import progress_utils
import traceback
import message
from PyQt6.QtCore import QCoreApplication
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def insert_demand_annotation_leader(color, draw0cmd):
    """Insert demand annotation leaders for all junctions."""
    df_junctions = globals.df_junctions
    df_node_results = globals.df_node_results
    
    try:

        for i in range(0, len(df_junctions)):
            id = df_junctions.at[i, 'ID']
            x = float(df_junctions.at[i, 'x'])
            y = float(df_junctions.at[i, 'y'])

            l = df_node_results.index[df_node_results['ID'] == id].tolist()[
                0]
            demand = df_node_results.at[l, 'Demand']

            if draw0cmd:
                draw_demand_leader(color=color, id=id, x=x, y=y, demand=demand,
                                   export0cmd=True, width=globals.line_width)
                msg = f'節點 {id} 需水量已完成繪圖'
                message.renew_message(msg, False)
                message.set_message_to_button()
                progress_utils.set_progress_bar(forced_value=None)
            else:
                draw_demand_leader(color=color, id=id, x=x, y=y, demand=demand,
                                   export0cmd=False, width=globals.line_width)
                msg = f'節點 {id} 需水量已完成繪圖'
                message.renew_message(msg, False)
                message.set_message_to_button()
                progress_utils.set_progress_bar(forced_value=None)

            QCoreApplication.processEvents()
    except Exception as e:
        traceback.print_exc()
        globals.logger.exception(e)


def draw_demand_leader(color, id, x, y, demand, export0cmd, width):
    """
    Draw a demand leader annotation arrow with text label showing water demand value.

    Args:
        color (int): Color code for the leader line and text
        id: Node identification
        x (float): X coordinate of the node
        y (float): Y coordinate of the node
        demand: Water demand value to display
        export0cmd (bool): Whether to export zero demand commands
        width (float): Width of the leader line
    """
    from ezdxf.enums import TextEntityAlignment

    text_size = globals.text_size
    leader_distance = globals.leader_distance
    block_size = globals.block_size
    msp = globals.msp

    try:

        if (export0cmd) or (export0cmd == False and float(demand) != 0.0):

            leader_down_start_x = x+0.5*text_size
            leader_down_start_y = y-0.5*text_size

            leader_down_end_x = leader_down_start_x+leader_distance
            leader_down_end_y = leader_down_start_y-leader_distance

            msp.add_blockref('demandArrow', [leader_down_end_x, leader_down_end_y],
                                     dxfattribs={'xscale': block_size, 'yscale': block_size, 'rotation': 225})
            msp.add_polyline2d([(leader_down_start_x, leader_down_start_y),
                                        (leader_down_end_x, leader_down_end_y)],
                                       dxfattribs={'color': color, 'default_start_width': width, 'default_end_width': width})
            msp.add_text(demand, height=text_size,
                                 dxfattribs={'color': color, "style": "epa2HydChart"})\
                .set_placement((leader_down_end_x+0.25*text_size, leader_down_end_y-0.25*text_size), align=TextEntityAlignment.TOP_LEFT)
        elif export0cmd == False and float(demand) == 0.0:
            pass
    except Exception as e:
        traceback.print_exc()
        globals.logger.exception(e)
