import globals
import message
import progress_utils
import traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow
    from ezdxf.document import Drawing


def create_blocks(cad: 'Drawing'):
    """Create block definitions for all hydraulic components"""
    try:
        tank_block = cad.blocks.new(name='tank')
        tank_block.add_polyline2d([(0.5, 0), (0.5, 0.5), (-0.5, 0.5), (-0.5, 0),
                                  (-0.25, 0), (-0.25, -0.5), (0.25, -0.5), (0.25, 0)], close=True)
        tank_block.add_hatch().paths.add_polyline_path(
            [(0.5, 0), (0.5, 0.5), (-0.5, 0.5), (-0.5, 0), (-0.25, 0), (-0.25, -0.5), (0.25, -0.5), (0.25, 0)], is_closed=True)

        reservoir_block = cad.blocks.new(name='reservoir')
        reservoir_block.add_polyline2d([(0.5, -0.25), (0.5, 0.5), (0.4, 0.5), (0.4, 0.25),
                                       (-0.4, 0.25), (-0.4, 0.5), (-0.5, 0.5), (-0.5, -0.25)], close=True)
        reservoir_block.add_hatch().paths.add_polyline_path(
            [(0.5, -0.25), (0.5, 0.5), (0.4, 0.5), (0.4, 0.25), (-0.4, 0.25), (-0.4, 0.5), (-0.5, 0.5), (-0.5, -0.25)], is_closed=True)

        junction_block = cad.blocks.new(name='junction')
        junction_block.add_ellipse((0, 0), major_axis=(0, 0.5), ratio=1)
        junction_block.add_hatch().paths.add_edge_path().add_ellipse(
            (0, 0), major_axis=(0, 0.5), ratio=1)

        valve_block = cad.blocks.new(name='valve')
        valve_block.add_polyline2d(
            [(0, 0), (0.5, 0.3), (0.5, -0.3)], close=True)
        valve_block.add_polyline2d(
            [(0, 0), (-0.5, 0.3), (-0.5, -0.3)], close=True)
        valve_block.add_hatch().paths.add_polyline_path(
            [(0, 0), (0.5, 0.3), (0.5, -0.3)], is_closed=True)
        valve_block.add_hatch().paths.add_polyline_path(
            [(0, 0), (-0.5, 0.3), (-0.5, -0.3)], is_closed=True)

        flow_direction_arrow_block = cad.blocks.new(name='flowDirectionArrow')
        flow_direction_arrow_block.add_polyline2d(
            [(0, 0), (-1, 0.25), (-1, -0.25)], close=True)
        flow_direction_arrow_block.add_hatch().paths.add_polyline_path(
            [(0, 0), (-1, 0.25), (-1, -0.25)], is_closed=True)

        from ezdxf.enums import TextEntityAlignment
        from ezdxf.math import Vec2
        pump_block = cad.blocks.new(name='pump')
        pump_block.add_circle(Vec2(0, 0), 0.5)
        pump_block.add_text("P", height=0.8, dxfattribs={"style": "epa2HydChart"}).set_placement(
            (0, 0), align=TextEntityAlignment.MIDDLE_CENTER)
    except Exception as e:
        traceback.print_exc()
        globals.logger.exception(e)


def insert_blocks(width):
    """Insert block references for all components at their locations."""
    try:
        mapping = {'tank': '水池',
                   'reservoir': '接水點',
                   'junction': '節點',
                   'pump': '抽水機',
                   'valve': '閥件'}

        df_mapping = {'tank': globals.df_tanks,
                      'reservoir': globals.df_reservoirs,
                      'junction': globals.df_junctions,
                      'pump': globals.df_pumps,
                      'valve': globals.df_valves}

        for item in ['tank', 'reservoir', 'junction', 'pump', 'valve']:
            if item == 'valve':
                import math
                df = globals.df_valves
                for i in range(0, len(df)):
                    id = df.at[i, 'ID']
                    x1 = float(df.at[i, 'Node1_x'])
                    y1 = float(df.at[i, 'Node1_y'])
                    x2 = float(df.at[i, 'Node2_x'])
                    y2 = float(df.at[i, 'Node2_y'])

                    x = 0.5 * (float(x1) + float(x2))
                    y = 0.5 * (float(y1) + float(y2))

                    rotation = math.atan2(y2-y1, x2-x1)
                    rotation = rotation * 180 / math.pi

                    globals.msp.add_blockref(item, [x, y], dxfattribs={
                                             'xscale': globals.block_size, 'yscale': globals.block_size, 'rotation': rotation})
                    globals.msp.add_polyline2d([(x1, y1), (x2, y2)], dxfattribs={
                                               'default_start_width': width, 'default_end_width': width})
                    msg = f'閥件 {id} 圖塊已插入'
                    message.renew_message(msg, False)
                    message.set_message_to_button()
                    progress_utils.set_progress_bar(forced_value=None)

            else:
                df = df_mapping[item]
                for i in range(0, len(df)):
                    id = df.at[i, 'ID']
                    x = float(df.at[i, 'x'])
                    y = float(df.at[i, 'y'])
                    if item == 'junction':
                        globals.msp.add_blockref(item, [x, y], dxfattribs={
                                                 'xscale': globals.joint_size, 'yscale': globals.joint_size})
                    else:
                        globals.msp.add_blockref(item, [x, y], dxfattribs={
                                                 'xscale': globals.block_size, 'yscale': globals.block_size})
                    msg = f'{mapping[item]} {id} 圖塊已插入'
                    message.renew_message(msg, False)
                    message.set_message_to_button()
                    progress_utils.set_progress_bar(forced_value=None)

    except Exception as e:
        traceback.print_exc()
        globals.logger.exception(e)
