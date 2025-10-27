import globals, log, progress_utils, traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow
    from ezdxf.document import Drawing

def create_blocks(cad: 'Drawing'):
    """Create block definitions for all hydraulic components"""
    try:
        tankBlock = cad.blocks.new(name='tank')
        tankBlock.add_polyline2d([(0.5,0), (0.5,0.5), (-0.5,0.5), (-0.5,0), (-0.25,0), (-0.25,-0.5), (0.25,-0.5), (0.25,0)], close=True)
        tankBlock.add_hatch().paths.add_polyline_path([(0.5,0), (0.5,0.5), (-0.5,0.5), (-0.5,0), (-0.25,0), (-0.25,-0.5), (0.25,-0.5), (0.25,0)], is_closed=True)

        reservoirBlock = cad.blocks.new(name='reservoir')
        reservoirBlock.add_polyline2d([(0.5,-0.25), (0.5,0.5), (0.4,0.5), (0.4,0.25), (-0.4,0.25), (-0.4,0.5), (-0.5,0.5), (-0.5,-0.25)], close=True)
        reservoirBlock.add_hatch().paths.add_polyline_path([(0.5,-0.25), (0.5,0.5), (0.4,0.5), (0.4,0.25), (-0.4,0.25), (-0.4,0.5), (-0.5,0.5), (-0.5,-0.25)], is_closed=True)

        junctionBlock = cad.blocks.new(name='junction')
        junctionBlock.add_ellipse((0,0), major_axis=(0,0.5), ratio=1)
        junctionBlock.add_hatch().paths.add_edge_path().add_ellipse((0,0), major_axis=(0,0.5), ratio=1)

        valveBlock = cad.blocks.new(name='valve')
        valveBlock.add_polyline2d([(0,0), (0.5,0.3), (0.5,-0.3)], close=True)
        valveBlock.add_polyline2d([(0,0), (-0.5,0.3), (-0.5,-0.3)], close=True)
        valveBlock.add_hatch().paths.add_polyline_path([(0,0), (0.5,0.3), (0.5,-0.3)], is_closed=True)
        valveBlock.add_hatch().paths.add_polyline_path([(0,0), (-0.5,0.3), (-0.5,-0.3)], is_closed=True)

        flowDirectionArrowBlock = cad.blocks.new(name='flowDirectionArrow')
        flowDirectionArrowBlock.add_polyline2d([(0,0), (-1,0.25), (-1,-0.25)], close=True)
        flowDirectionArrowBlock.add_hatch().paths.add_polyline_path([(0,0), (-1,0.25), (-1,-0.25)], is_closed=True)

        from ezdxf.enums import TextEntityAlignment
        from ezdxf.math import Vec2
        pumpBlock = cad.blocks.new(name='pump')
        pumpBlock.add_circle(Vec2(0,0), 0.5)
        pumpBlock.add_text("P", height=0.8, dxfattribs={"style": "epa2HydChart"}).set_placement((0,0), align=TextEntityAlignment.MIDDLE_CENTER)
    except Exception as e:
        traceback.print_exc()

def insert_blocks(*args, **kwargs):
    """Insert block references for all components at their locations"""
    try:
        width = kwargs.get('width')
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
                    id = df.at[i,'ID']
                    x1 = float(df.at[i,'Node1_x'])
                    y1 = float(df.at[i,'Node1_y'])
                    x2 = float(df.at[i,'Node2_x'])
                    y2 = float(df.at[i,'Node2_y'])

                    x = 0.5 * (float(x1) + float(x2))
                    y = 0.5 * (float(y1) + float(y2))

                    rotation = math.atan2(y2-y1, x2-x1)
                    rotation = rotation * 180 / math.pi

                    globals.msp.add_blockref(item, [x,y], dxfattribs={'xscale':globals.block_size, 'yscale':globals.block_size, 'rotation':rotation})
                    globals.msp.add_polyline2d([(x1,y1), (x2,y2)], dxfattribs={'default_start_width': width, 'default_end_width': width})
                    msg = f'閥件 {id} 圖塊已插入'
                    log.renew_log(msg, False)
                    log.set_log_to_button()
                    progress_utils.set_progress(ForcedValue=None)

            else:
                df = df_mapping[item]
                for i in range(0, len(df)):
                    id = df.at[i,'ID']
                    x = float(df.at[i,'x'])
                    y = float(df.at[i,'y'])
                    if item == 'junction':
                        globals.msp.add_blockref(item, [x,y], dxfattribs={'xscale':globals.joint_size, 'yscale':globals.joint_size})
                    else:
                        globals.msp.add_blockref(item, [x,y], dxfattribs={'xscale':globals.block_size, 'yscale':globals.block_size})
                    msg = f'{mapping[item]} {id} 圖塊已插入'
                    log.renew_log(msg, False)
                    log.set_log_to_button()
                    progress_utils.set_progress(ForcedValue=None)

    except Exception as e:
        traceback.print_exc()
