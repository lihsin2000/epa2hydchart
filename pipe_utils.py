import globals
import progress_utils
import traceback
import message
import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def pipe_annotation_block(link_id, start_x, start_y, end_x, end_y, i, pipe_boundaries):
    """Create pipe annotation block with flow direction and store boundary for overlap detection."""
    
    df_pipes = globals.df_pipes
    df_link_results = globals.df_link_results
    msp = globals.msp
    text_size = globals.text_size

    try:
        center_x = (start_x+end_x)/2
        center_y = (start_y+end_y)/2
        diameter = df_pipes.at[i, 'Diameter']
        length = df_pipes.at[i, 'Length']

        link_row = df_link_results.index[df_link_results['ID'] == link_id].tolist()[
            0]
        flow = float(df_link_results.at[link_row, 'Flow'])

        import math
        rotation = math.atan2(end_y-start_y, end_x-start_x)
        rotation = math.degrees(rotation)

        if rotation < 0:
            rotation += 360

        if rotation > 90 and rotation < 270:
            rotation_annotaion = rotation-180
        else:
            rotation_annotaion = rotation

        headloss = df_link_results.at[link_row, 'Headloss']

        attrib = {"char_height": text_size,
                  "style": "epa2HydChart",
                  "attachment_point": 5,
                  "line_spacing_factor": 1,
                  'rotation': rotation_annotaion}

        text = f"""{diameter}-{length}\n{abs(flow)} ({headloss})"""

        msp.add_mtext(text, dxfattribs=attrib).set_location(
            insert=(center_x, center_y))

        # Calculate approximate text bounding box (2 lines of text)
        line1_len = len(f"{diameter}-{length}")
        line2_len = len(f"{abs(flow)} ({headloss})")
        max_chars = max(line1_len, line2_len)

        # Approximate dimensions (character width ~0.6 * text_size, 2 lines with spacing)
        text_width = max_chars * 0.6 * text_size
        text_height = 2.5 * text_size  # 2 lines plus spacing

        # Store pipe annotation boundary in SAT format
        pipe_boundary = {
            'id': link_id,
            'rect': (center_x, center_y, text_width, text_height, rotation_annotaion)
        }
        pipe_boundaries.append(pipe_boundary)

        if flow >= 0:
            msp.add_blockref('flowDirectionArrow', [center_x, center_y], dxfattribs={
                                     'xscale': text_size, 'yscale': text_size, 'rotation': rotation})
        else:
            msp.add_blockref('flowDirectionArrow', [center_x, center_y], dxfattribs={
                                     'xscale': text_size, 'yscale': text_size, 'rotation': rotation+180})

    except Exception as e:
        msg = f'[Error]管線 {link_id} 錯誤，請重新匯出inp及rpt檔後重試'
        message.renew_message(msg, True)
        traceback.print_exc()
        globals.logger.exception(e)


def insert_pipe_annotation():
    """Insert pipe annotations and collect their boundaries for overlap detection."""
    
    df_pipes = globals.df_pipes
    df_vertices = globals.df_vertices
    
    pipe_boundaries = []

    try:
        # Convert LINK column to set for O(1) lookups
        link_ids = set(df_vertices['LINK'])

        # Group by LINK for fast access
        vertices_dict = df_vertices.groupby('LINK')[['x', 'y']].apply(
            lambda g: list(zip(g['x'], g['y']))).to_dict()

        for i, row in df_pipes.iterrows():
            link_id = row['ID']

            if link_id in link_ids:
                verts = vertices_dict[link_id]
                num_verts = len(verts)

                if num_verts == 1:  # 1 vertex
                    start_x, start_y = float(
                        row['Node1_x']), float(row['Node1_y'])
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
            pipe_annotation_block(link_id, start_x, start_y,
                                  end_x, end_y, i, pipe_boundaries)
            # msg= f'管線 {link_id} 已插入標示'
            # log.renew_log(msg, False)
            # log.setLogToButton()
            # progress_utils.setProgress(ForcedValue=None)
    except Exception as e:
        traceback.print_exc()
        globals.logger.exception(e)

    # Always return a list, even if empty
    return pipe_boundaries if pipe_boundaries else []


def calculate_text_rotation_angle(start_x, start_y, end_x, end_y):
    """Calculate appropriate text rotation angle based on pipe direction."""
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
        globals.logger.exception(e)


def draw_pipe_polylines(width):
    """Draw pipe polylines including vertices if available."""
    from PyQt6.QtCore import QCoreApplication
    
    df_pipes = globals.df_pipes
    df_vertices = globals.df_vertices
    msp = globals.msp

    try:

        for i in range(0, len(df_pipes)):
            start_x = float(df_pipes.at[i, 'Node1_x'])
            start_y = float(df_pipes.at[i, 'Node1_y'])
            end_x = float(df_pipes.at[i, 'Node2_x'])
            end_y = float(df_pipes.at[i, 'Node2_y'])

            link_id = df_pipes.at[i, 'ID']
            if link_id in df_vertices['LINK'].tolist():
                rows = df_vertices.index[df_vertices['LINK'] == link_id].tolist(
                )
                firstVert_x = float(df_vertices.at[rows[0], 'x'])
                firstVert_y = float(df_vertices.at[rows[0], 'y'])
                msp.add_polyline2d([(start_x, start_y), (firstVert_x, firstVert_y)], dxfattribs={
                                           'default_start_width': width, 'default_end_width': width})
                for j in rows[:len(rows)-1]:
                    x1 = float(df_vertices.at[j, 'x'])
                    y1 = float(df_vertices.at[j, 'y'])
                    x2 = float(df_vertices.at[j+1, 'x'])
                    y2 = float(df_vertices.at[j+1, 'y'])
                    msp.add_polyline2d([(x1, y1), (x2, y2)], dxfattribs={
                                               'default_start_width': width, 'default_end_width': width})

                lastVert_x = float(
                    df_vertices.at[rows[len(rows)-1], 'x'])
                lastVert_y = float(
                    df_vertices.at[rows[len(rows)-1], 'y'])
                msp.add_polyline2d([(lastVert_x, lastVert_y), (end_x, end_y)], dxfattribs={
                                           'default_start_width': width, 'default_end_width': width})
            else:
                msp.add_polyline2d([(end_x, end_y), (start_x, start_y)], dxfattribs={
                                           'default_start_width': width, 'default_end_width': width})

            msg = f'管線 {link_id} 已完成繪圖'
            message.renew_message(msg, False)
            message.set_message_to_button()
            progress_utils.set_progress_bar(forced_value=None)
            QCoreApplication.processEvents()
    except Exception as e:
        traceback.print_exc()
        globals.logger.exception(e)
