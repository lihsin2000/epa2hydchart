import globals, progress_utils, traceback
import log
import SATdetect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def insertHeadPressureLeader(*args, **kwargs):
    from ezdxf.enums import TextEntityAlignment
    HeadColor=kwargs.get('HeadColor')
    ElevColor=kwargs.get('ElevColor')
    width=kwargs.get('width')
    autoLabelPost=kwargs.get('autoLabelPost')

    boundrys:dict=[]
    try:
        for i in range(0, len(globals.df_Junctions)):
            id = globals.df_Junctions.at[i, 'ID']
            start_x = float(globals.df_Junctions.at[i, 'x'])
            start_y = float(globals.df_Junctions.at[i, 'y'])
            result_row = globals.df_NodeResults.index[globals.df_NodeResults['ID'] == str(id)].tolist()[0]
            Head = globals.df_NodeResults.at[result_row, 'Head']
            Elev = globals.df_Junctions.at[i, 'Elev']
            Pressure = globals.df_NodeResults.at[result_row, 'Pressure']

            if (Pressure == None) or (float(Pressure)<0):
                PressureColor=1
            else:
                PressureColor=HeadColor

            if (Head == None) or (float(Head)<0):
                HeadColor=1
            else:
                HeadColor=HeadColor

            line_attribs={'color': HeadColor, 'default_start_width': width, 'default_end_width': width}
            Head_attribs={'color': HeadColor, "style": "epa2HydChart"}
            Pressure_attribs={'color': PressureColor, "style": "epa2HydChart"}
            Elev_attribs={'color': ElevColor, "style": "epa2HydChart"}

            parameters={'Head':Head, 'Elev':Elev, 'Pressure':Pressure,
                        'start_x':start_x, 'start_y':start_y,
                        'line_attribs':line_attribs,
                        'Head_attribs':Head_attribs,
                        'Elev_attribs':Elev_attribs,
                        'Pressure_attribs':Pressure_attribs}

            if autoLabelPost:
                new_boundry=CreateNewBoundry(start_x=start_x, start_y=start_y, align="RightTop", id=id)
                isOverlap=isOverlapWithAnyBounery(new_boundry=new_boundry, boundrys=boundrys, id=id, verbose=True)
                if isOverlap == False:
                    DrawLeader(parameters=parameters, align="RightTop")
                    DrawBoundry(boundry=new_boundry)
                else:
                    new_boundry=CreateNewBoundry(start_x=start_x, start_y=start_y, align="LeftTop", id=id)
                    isOverlap=isOverlapWithAnyBounery(new_boundry=new_boundry, boundrys=boundrys, id=id, verbose=True)
                    if isOverlap == False:
                        DrawLeader(parameters=parameters, align="LeftTop")
                        DrawBoundry(boundry=new_boundry)
                    else:
                        new_boundry=CreateNewBoundry(start_x=start_x, start_y=start_y, align="LeftBottom", id=id)
                        DrawLeader(parameters=parameters, align="LeftBottom")
                        DrawBoundry(boundry=new_boundry)

                boundrys.append(new_boundry)
            else:
                DrawLeader(parameters=parameters, align="RightTop")
            msg= f'節點 {id} 水頭引線已完成繪圖'
            log.renew_log(msg, False)
            log.setLogToButton()
            progress_utils.setProgress(ForcedValue=None)
    except Exception as e:
        traceback.print_exc()

def CreateNewBoundry(*args, **kwargs) -> dict:
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

def DrawBoundry(*args, **kwargs):
    start_x = kwargs.get('boundry')['start_x']
    start_y = kwargs.get('boundry')['start_y']
    end_x = kwargs.get('boundry')['end_x']
    end_y = kwargs.get('boundry')['end_y']

    globals.msp.add_lwpolyline([(start_x, start_y), (end_x, start_y), (end_x, end_y), (start_x, end_y), (start_x, start_y)],
                                dxfattribs={'color': 7})

def isOverlapWithAnyBounery(new_boundry: dict, boundrys: list, id, verbose) -> bool:
    """
    Check if new boundary overlaps with any existing boundaries using SAT algorithm.
    More accurate than corner-based detection, especially for rotated rectangles.
    """
    if boundrys == []:
        return False
    
    new_rect = new_boundry['rect']
    
    for boundry in boundrys:
        existing_rect = boundry['rect']
        
        # Use SAT algorithm for overlap detection
        if SATdetect.rectangles_overlap(new_rect, existing_rect):
            if verbose:
                print(f'{id} 與 {boundry["id"]} 節點引線重疊，改變繪圖位置')
            return True
    
    # No overlap found with any boundary
    return False

def DrawLeader(*args, **kwargs):
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
