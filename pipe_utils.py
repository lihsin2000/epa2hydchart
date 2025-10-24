import globals, progress_utils, traceback
import log
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow

def pipeAnnotationBlock(link_id, start_x, start_y, end_x, end_y, i):
    try:
        center_x=(start_x+end_x)/2
        center_y=(start_y+end_y)/2
        diameter=globals.df_Pipes.at[i, 'Diameter']
        length=globals.df_Pipes.at[i, 'Length']

        link_row=globals.df_LinkResults.index[globals.df_LinkResults['ID']==link_id].tolist()[0]
        flow=float(globals.df_LinkResults.at[link_row, 'Flow'])

        import math
        rotation=math.atan2(end_y-start_y, end_x-start_x)
        rotation=math.degrees(rotation)

        if rotation<0:
            rotation+=360

        if rotation > 90 and rotation < 270:
            rotation_annotaion=rotation-180
        else:
            rotation_annotaion=rotation

        headloss=globals.df_LinkResults.at[link_row, 'Headloss']

        attrib={"char_height": globals.text_size,
                "style": "epa2HydChart",
                "attachment_point":5,
                "line_spacing_factor":1.5,
                'rotation':rotation_annotaion}

        text=f"""{diameter}-{length}\n{abs(flow)} ({headloss})"""

        globals.msp.add_mtext(text, dxfattribs=attrib).set_location(insert=(center_x, center_y))

        if flow>=0:
            globals.msp.add_blockref('flowDirectionArrow', [center_x,center_y], dxfattribs={'xscale':globals.text_size, 'yscale':globals.text_size, 'rotation':rotation})
        else:
            globals.msp.add_blockref('flowDirectionArrow', [center_x,center_y], dxfattribs={'xscale':globals.text_size, 'yscale':globals.text_size, 'rotation':rotation+180})

    except Exception as e:
        print(e)
        msg=f'[Error]管線 {link_id} 錯誤，請重新匯出inp及rpt檔後重試'
        log.renew_log(msg, True)
        traceback.print_exc()

def insertPipeAnnotation():
    try:
        # Convert LINK column to set for O(1) lookups
        link_ids = set(globals.df_Vertices['LINK'])

        # Group by LINK for fast access
        vertices_dict = globals.df_Vertices.groupby('LINK')[['x', 'y']].apply(lambda g: list(zip(g['x'], g['y']))).to_dict()

        for i, row in globals.df_Pipes.iterrows():
            link_id = row['ID']

            if link_id in link_ids:
                verts = vertices_dict[link_id]
                num_verts = len(verts)

                if num_verts == 1:  # 1 vertex
                    start_x, start_y = float(row['Node1_x']), float(row['Node1_y'])
                    end_x, end_y = verts[0]  # First and only vertex

                elif num_verts % 2 == 0:  # Even number of vertices
                    mid = num_verts // 2
                    start_x, start_y = verts[mid - 1]
                    end_x, end_y = verts[mid]

                else:  # Odd number of vertices
                    mid = num_verts // 2
                    start_x, start_y = verts[mid - 1]
                    end_x, end_y = verts[mid]

            else:  # No vertices
                start_x, start_y = float(row['Node1_x']), float(row['Node1_y'])
                end_x, end_y = float(row['Node2_x']), float(row['Node2_y'])

            # Call annotation function once per pipe
            pipeAnnotationBlock(link_id, start_x, start_y, end_x, end_y, i)
            # msg= f'管線 {link_id} 已插入標示'
            # log.renew_log(msg, False)
            # log.setLogToButton()
            # progress_utils.setProgress(ForcedValue=None)
    except Exception as e:
        traceback.print_exc()

def rotation_text(start_x, start_y, end_x, end_y):
    import math
    try:
        rotation = math.atan2(end_y-start_y, end_x-start_x)
        rotation = math.degrees(rotation)
        if rotation < 0:
            rotation += 360
        if 90 < rotation < 270:
            rotation_text = rotation-180
        else:
            rotation_text = rotation
        return rotation_text
    except Exception as e:
        traceback.print_exc()

def insertPipeLines(*args, **kwargs):
    from PyQt6.QtCore import QCoreApplication
    try:
        width=kwargs.get('width')

        for i in range(0, len(globals.df_Pipes)):
            start_x=float(globals.df_Pipes.at[i, 'Node1_x'])
            start_y=float(globals.df_Pipes.at[i, 'Node1_y'])
            end_x=float(globals.df_Pipes.at[i, 'Node2_x'])
            end_y=float(globals.df_Pipes.at[i, 'Node2_y'])

            link_id=globals.df_Pipes.at[i, 'ID']
            if link_id in globals.df_Vertices['LINK'].tolist():
                rows=globals.df_Vertices.index[globals.df_Vertices['LINK']==link_id].tolist()
                firstVert_x=float(globals.df_Vertices.at[rows[0],'x'])
                firstVert_y=float(globals.df_Vertices.at[rows[0],'y'])
                globals.msp.add_polyline2d([(start_x,start_y), (firstVert_x,firstVert_y)], dxfattribs={'default_start_width': width, 'default_end_width': width})
                for j in rows[:len(rows)-1]:
                    x1=float(globals.df_Vertices.at[j,'x'])
                    y1=float(globals.df_Vertices.at[j,'y'])
                    x2=float(globals.df_Vertices.at[j+1,'x'])
                    y2=float(globals.df_Vertices.at[j+1,'y'])
                    globals.msp.add_polyline2d([(x1,y1), (x2,y2)], dxfattribs={'default_start_width': width, 'default_end_width': width})
            
                lastVert_x=float(globals.df_Vertices.at[rows[len(rows)-1],'x'])
                lastVert_y=float(globals.df_Vertices.at[rows[len(rows)-1],'y'])
                globals.msp.add_polyline2d([(lastVert_x,lastVert_y), (end_x,end_y)], dxfattribs={'default_start_width': width, 'default_end_width': width})
            else:
                globals.msp.add_polyline2d([(end_x,end_y), (start_x,start_y)], dxfattribs={'default_start_width': width, 'default_end_width': width})

            msg= f'管線 {link_id} 已完成繪圖'
            log.renew_log(msg, False)
            log.setLogToButton()
            progress_utils.setProgress(ForcedValue=None)
            QCoreApplication.processEvents()
    except Exception as e:
        traceback.print_exc()
