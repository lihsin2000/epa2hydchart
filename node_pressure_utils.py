import globals, progress_utils, traceback
import log
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def insertHeadPressureLeader(*args, **kwargs):
    from ezdxf.enums import TextEntityAlignment
    HeadColor=kwargs.get('HeadColor')
    ElevColor=kwargs.get('ElevColor')
    width=kwargs.get('width')

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

            boundrys=None

            new_boundry=CreateBoundry(start_x=start_x, start_y=start_y, align="RightTop", id=id)


            DrawLeader(Head=Head, Elev=Elev, Pressure=Pressure,
                       start_x=start_x, start_y=start_y,
                       line_attribs=line_attribs,
                       Head_attribs=Head_attribs,
                       Elev_attribs=Elev_attribs,
                       Pressure_attribs=Pressure_attribs,
                       align="RightTop")

            msg= f'節點 {id} 水頭引線已完成繪圖'
            log.renew_log(msg, False)
            log.setLogToButton()
            progress_utils.setProgress(ForcedValue=None)
    except Exception as e:
        traceback.print_exc()

def CreateBoundry(*args, **kwargs) -> dict:
    start_x = kwargs.get('start_x')
    start_y = kwargs.get('start_y')
    align = kwargs.get('align')
    id = kwargs.get('id')

    end_x = start_x + globals.text_size + globals.leader_distance+6*globals.text_size
    end_y = start_y + globals.text_size + globals.leader_distance+3*globals.text_size

    dic = {'id': id, 'start_x': start_x, 'start_y': start_y, 'end_x': end_x, 'end_y': end_y}
    return dic

def CheckOverlap(new_boundry: dict, boundrys: list) -> bool:
    pass

def DrawLeader(*args, **kwargs):
    from ezdxf.enums import TextEntityAlignment
    Head = kwargs.get('Head')
    Elev = kwargs.get('Elev')
    Pressure = kwargs.get('Pressure')
    start_x = kwargs.get('start_x')
    start_y = kwargs.get('start_y')
    line_attribs = kwargs.get('line_attribs')
    Head_attribs = kwargs.get('Head_attribs')
    Elev_attribs = kwargs.get('Elev_attribs')
    Pressure_attribs = kwargs.get('Pressure_attribs')
    align=kwargs.get('align')

    if align == "RightTop":
        leader_up_start_x = start_x + globals.text_size
        leader_up_start_y = start_y + globals.text_size

        leader_up_end_x = leader_up_start_x + globals.leader_distance
        leader_up_end_y = leader_up_start_y + globals.leader_distance

        line_x1, line_y1 = leader_up_start_x, leader_up_start_y
        line_x2, line_y2 = leader_up_end_x, leader_up_end_y
        line_x3, line_y3 = leader_up_end_x+6*globals.text_size, leader_up_end_y

        text_start_x = line_x3

    elif align == "LeftTop":
        leader_up_start_x = start_x - globals.text_size
        leader_up_start_y = start_y + globals.text_size

        leader_up_end_x = leader_up_start_x - globals.leader_distance
        leader_up_end_y = leader_up_start_y + globals.leader_distance

        line_x1, line_y1 = leader_up_start_x, leader_up_start_y
        line_x2, line_y2 = leader_up_end_x, leader_up_end_y
        line_x3, line_y3 = leader_up_end_x-6*globals.text_size, leader_up_end_y

        text_start_x = line_x3+6*globals.text_size

    elif align == "LeftBottom":
        leader_up_start_x = start_x - globals.text_size
        leader_up_start_y = start_y - globals.text_size

        leader_up_end_x = leader_up_start_x - globals.leader_distance
        leader_up_end_y = leader_up_start_y - globals.leader_distance

        line_x1, line_y1 = leader_up_start_x, leader_up_start_y
        line_x2, line_y2 = leader_up_end_x, leader_up_end_y
        line_x3, line_y3 = leader_up_end_x-6*globals.text_size, leader_up_end_y

        text_start_x = line_x3+6*globals.text_size
    
    Head_placement_y= leader_up_end_y + 2 * globals.text_size
    Elev_placement_y= leader_up_end_y + 0.75 * globals.text_size
    Pressure_placement_y= leader_up_end_y - 0.75 * globals.text_size

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