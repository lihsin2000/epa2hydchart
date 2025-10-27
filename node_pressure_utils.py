import globals, progress_utils, traceback
import log
import SATdetect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def insert_pressure_annotation_leader(*args, **kwargs):
    from ezdxf.enums import TextEntityAlignment
    head_color=kwargs.get('HeadColor')
    elev_color=kwargs.get('ElevColor')
    width=kwargs.get('width')
    auto_label_post=kwargs.get('autoLabelPost')
    pipe_boundaries=kwargs.get('pipe_boundaries', [])
    draw_boundaries=kwargs.get('drawBoundaries')

    boundrys:dict=[]
    try:
        for i in range(0, len(globals.df_junctions)):
            id = globals.df_junctions.at[i, 'ID']
            start_x = float(globals.df_junctions.at[i, 'x'])
            start_y = float(globals.df_junctions.at[i, 'y'])
            result_row = globals.df_node_results.index[globals.df_node_results['ID'] == str(id)].tolist()[0]
            Head = globals.df_node_results.at[result_row, 'Head']
            Elev = globals.df_junctions.at[i, 'Elev']
            Pressure = globals.df_node_results.at[result_row, 'Pressure']

            if (Pressure == None) or (float(Pressure)<0):
                pressure_color=1
            else:
                pressure_color=head_color

            if (Head == None) or (float(Head)<0):
                head_color_used=1
            else:
                head_color_used=head_color

            line_attribs={'color': head_color_used, 'default_start_width': width, 'default_end_width': width}
            Head_attribs={'color': head_color_used, "style": "epa2HydChart"}
            Pressure_attribs={'color': pressure_color, "style": "epa2HydChart"}
            Elev_attribs={'color': elev_color, "style": "epa2HydChart"}

            parameters={'Head':Head, 'Elev':Elev, 'Pressure':Pressure,
                        'start_x':start_x, 'start_y':start_y,
                        'line_attribs':line_attribs,
                        'Head_attribs':Head_attribs,
                        'Elev_attribs':Elev_attribs,
                        'Pressure_attribs':Pressure_attribs}

            if auto_label_post:
                new_boundry=create_new_boundary(start_x=start_x, start_y=start_y, align="RightTop", id=id)
                # Check overlap with both node boundaries and pipe annotations
                is_overlap=is_pressure_annotation_overlapping_any_boundary(new_boundry=new_boundry, boundrys=boundrys, pipe_boundaries=pipe_boundaries, id=id, verbose=True)
                if is_overlap == False:
                    draw_pressure_annotation_leader(parameters=parameters, align="RightTop")
                    draw_pressure_boundary(boundry=new_boundry) if draw_boundaries else None
                else:
                    new_boundry=create_new_boundary(start_x=start_x, start_y=start_y, align="LeftTop", id=id)
                    is_overlap=is_pressure_annotation_overlapping_any_boundary(new_boundry=new_boundry, boundrys=boundrys, pipe_boundaries=pipe_boundaries, id=id, verbose=True)
                    if is_overlap == False:
                        draw_pressure_annotation_leader(parameters=parameters, align="LeftTop")
                        draw_pressure_boundary(boundry=new_boundry) if draw_boundaries else None
                    else:
                        new_boundry=create_new_boundary(start_x=start_x, start_y=start_y, align="LeftBottom", id=id)
                        draw_pressure_annotation_leader(parameters=parameters, align="LeftBottom")
                        draw_pressure_boundary(boundry=new_boundry) if draw_boundaries else None

                boundrys.append(new_boundry)
            else:
                draw_pressure_annotation_leader(parameters=parameters, align="RightTop")
            msg= f'節點 {id} 水頭引線已完成繪圖'
            log.renew_log(msg, False)
            log.set_log_to_button()
            progress_utils.set_progress_bar(forced_value=None)
    except Exception as e:
        traceback.print_exc()

def create_new_boundary(*args, **kwargs) -> dict:
    """
    Create boundary rectangle for SAT overlap detection.
    Returns: dict with 'id' and 'rect' tuple (cx, cy, w, h, angle_deg)
    """
    original_x = kwargs.get('start_x')
    original_y = kwargs.get('start_y')
    align = kwargs.get('align')
    id = kwargs.get('id')

    if align == "RightTop":
        start_x = original_x + globals.text_size + globals.leader_distance
        start_y = original_y + globals.text_size + globals.leader_distance-2*globals.text_size
        end_x = original_x + globals.text_size + globals.leader_distance+6*globals.text_size
        end_y = original_y + globals.text_size + globals.leader_distance+3*globals.text_size
    elif align == "LeftTop":
        start_x = original_x - globals.text_size - globals.leader_distance
        start_y = original_y + globals.text_size + globals.leader_distance-2*globals.text_size
        end_x = original_x - globals.text_size - globals.leader_distance - 6 * globals.text_size
        end_y = original_y + globals.text_size + globals.leader_distance+3*globals.text_size
    elif align == "LeftBottom":
        start_x = original_x - globals.text_size - globals.leader_distance
        start_y = original_y - globals.text_size - globals.leader_distance + 3 * globals.text_size
        end_x = original_x - globals.text_size - globals.leader_distance - 6 * globals.text_size
        end_y = original_y - globals.text_size - globals.leader_distance - 2 * globals.text_size

    # Convert to SAT rectangle format: (center_x, center_y, width, height, angle_deg)
    cx = (start_x + end_x) / 2
    cy = (start_y + end_y) / 2
    w = abs(end_x - start_x)
    h = abs(end_y - start_y)
    angle_deg = 0  # Axis-aligned rectangles
    
    dic = {
        'id': id, 
        'start_x': start_x, 'start_y': start_y, 
        'end_x': end_x, 'end_y': end_y,
        'rect': (cx, cy, w, h, angle_deg)  # SAT format
    }

    return dic

def draw_pressure_boundary(*args, **kwargs):
    start_x = kwargs.get('boundry')['start_x']
    start_y = kwargs.get('boundry')['start_y']
    end_x = kwargs.get('boundry')['end_x']
    end_y = kwargs.get('boundry')['end_y']

    globals.msp.add_lwpolyline([(start_x, start_y), (end_x, start_y), (end_x, end_y), (start_x, end_y), (start_x, start_y)],
                                dxfattribs={'color': 7})

def is_pressure_annotation_overlapping_any_boundary(new_boundry: dict, boundrys: list, pipe_boundaries: list, id, verbose) -> bool:
    """
    Check if new boundary overlaps with any existing boundaries (nodes and pipes) using SAT algorithm.
    More accurate than corner-based detection, especially for rotated rectangles.
    """
    new_rect = new_boundry['rect']
    
    # Check overlap with node pressure boundaries
    for boundry in boundrys:
        existing_rect = boundry['rect']
        
        # Use SAT algorithm for overlap detection
        if SATdetect.rectangles_overlap(new_rect, existing_rect):
            if verbose:
                print(f'節點{id} 標示與節點 {boundry["id"]} 引線重疊，改變繪圖位置')
            return True
    
    # Check overlap with pipe annotation boundaries
    for pipe_boundary in pipe_boundaries:
        pipe_rect = pipe_boundary['rect']
        
        # Use SAT algorithm for overlap detection
        if SATdetect.rectangles_overlap(new_rect, pipe_rect):
            if verbose:
                print(f'節點 {id} 標示與管線 {pipe_boundary["id"]} 標註重疊，改變繪圖位置')
            return True
    
    # No overlap found with any boundary
    return False

def draw_pressure_annotation_leader(*args, **kwargs):
    from ezdxf.enums import TextEntityAlignment
    Head = kwargs.get('parameters')['Head']
    Elev = kwargs.get('parameters')['Elev']
    Pressure = kwargs.get('parameters')['Pressure']
    start_x = kwargs.get('parameters')['start_x']
    start_y = kwargs.get('parameters')['start_y']
    line_attribs = kwargs.get('parameters')['line_attribs']
    Head_attribs = kwargs.get('parameters')['Head_attribs']
    Elev_attribs = kwargs.get('parameters')['Elev_attribs']
    Pressure_attribs = kwargs.get('parameters')['Pressure_attribs']

    align=kwargs.get('align')

    if align == "RightTop":
  
        line_x1, line_y1 = start_x + globals.text_size, start_y + globals.text_size
        line_x2, line_y2 = line_x1+globals.leader_distance, line_y1+globals.leader_distance
        line_x3, line_y3 = line_x2+6*globals.text_size, line_y2

        text_start_x = line_x3

    elif align == "LeftTop":
        line_x1, line_y1 = start_x - globals.text_size, start_y + globals.text_size
        line_x2, line_y2 = line_x1 - globals.leader_distance, line_y1 + globals.leader_distance
        line_x3, line_y3 = line_x2 - 6 * globals.text_size, line_y2

        text_start_x = line_x3 + 6 * globals.text_size

    elif align == "LeftBottom":
        line_x1, line_y1 = start_x - globals.text_size, start_y - globals.text_size
        line_x2, line_y2 = line_x1 - globals.leader_distance, line_y1 - globals.leader_distance
        line_x3, line_y3 = line_x2 - 6 * globals.text_size, line_y2

        text_start_x = line_x3 + 6 * globals.text_size
    
    Head_placement_y= line_y3 + 2 * globals.text_size
    Elev_placement_y= line_y3 + 0.75 * globals.text_size
    Pressure_placement_y= line_y3 - 0.75 * globals.text_size

    globals.msp.add_polyline2d([(line_x1, line_y1), (line_x2, line_y2), (line_x3, line_y3)], dxfattribs=line_attribs)

    Head_placement = text_start_x, Head_placement_y
    globals.msp.add_text(Head, height = globals.text_size,
                            dxfattribs=Head_attribs).set_placement(Head_placement, align = TextEntityAlignment.MIDDLE_RIGHT)

    Elev_placement = text_start_x, Elev_placement_y
    globals.msp.add_text(Elev, height = globals.text_size,
                            dxfattribs = Elev_attribs).set_placement(Elev_placement, align = TextEntityAlignment.MIDDLE_RIGHT)
    
    Pressure_placement = text_start_x, Pressure_placement_y
    globals.msp.add_text(Pressure, height = globals.text_size,
                            dxfattribs = Pressure_attribs).set_placement(Pressure_placement, align = TextEntityAlignment.MIDDLE_RIGHT)
