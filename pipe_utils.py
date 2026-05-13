import globals
import progress_utils
import traceback
import message
import math
import SATdetect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def pipe_annotation_block(link_id, segments, preferred_idx, i, pipe_boundaries, auto_label_post=False):
    """Create pipe annotation block with flow direction and store boundary for overlap detection."""

    df_pipes = globals.df_pipes
    df_link_results = globals.df_link_results
    msp = globals.msp
    text_size = globals.text_size

    try:
        diameter = df_pipes.at[i, 'Diameter']
        length = df_pipes.at[i, 'Length']

        link_row = df_link_results.index[df_link_results['ID'] == link_id].tolist()[0]
        flow = float(df_link_results.at[link_row, 'Flow'])
        headloss = df_link_results.at[link_row, 'Headloss']

        text = f"""{diameter}-{length}\n{abs(flow)} ({headloss})"""
        line1_len = len(f"{diameter}-{length}")
        line2_len = len(f"{abs(flow)} ({headloss})")
        max_chars = max(line1_len, line2_len)
        text_width = max_chars * 0.6 * text_size
        text_height = 2.5 * text_size

        # Try each candidate segment, use first non-overlapping position
        chosen_idx = preferred_idx
        if auto_label_post:
            n = len(segments)
            order = []
            for step in range(n):
                if step == 0:
                    order.append(preferred_idx)
                else:
                    if preferred_idx - step >= 0:
                        order.append(preferred_idx - step)
                    if preferred_idx + step < n:
                        order.append(preferred_idx + step)

            for idx in order:
                (sx, sy), (ex, ey) = segments[idx]
                cx = (sx + ex) / 2
                cy = (sy + ey) / 2
                rot = math.degrees(math.atan2(ey - sy, ex - sx))
                if rot < 0:
                    rot += 360
                rot_ann = rot - 180 if 90 < rot < 270 else rot
                candidate = (cx, cy, text_width, text_height, rot_ann)
                if not any(SATdetect.rectangles_overlap(candidate, p['rect']) for p in pipe_boundaries):
                    chosen_idx = idx
                    break

        (start_x, start_y), (end_x, end_y) = segments[chosen_idx]
        center_x = (start_x + end_x) / 2
        center_y = (start_y + end_y) / 2
        rotation = math.degrees(math.atan2(end_y - start_y, end_x - start_x))
        if rotation < 0:
            rotation += 360
        rotation_annotaion = rotation - 180 if 90 < rotation < 270 else rotation

        attrib = {"char_height": text_size,
                  "style": "epa2HydChart",
                  "attachment_point": 5,
                  "line_spacing_factor": 1,
                  'rotation': rotation_annotaion}

        msp.add_mtext(text, dxfattribs=attrib).set_location(insert=(center_x, center_y))

        pipe_boundaries.append({
            'id': link_id,
            'rect': (center_x, center_y, text_width, text_height, rotation_annotaion)
        })

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


def insert_pipe_annotation(auto_label_post=False):
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
            node1 = (float(row['Node1_x']), float(row['Node1_y']))
            node2 = (float(row['Node2_x']), float(row['Node2_y']))

            if link_id in link_ids:
                verts = vertices_dict[link_id]
                points = [node1] + list(verts) + [node2]
            else:
                points = [node1, node2]

            segments = [(points[k], points[k + 1]) for k in range(len(points) - 1)]
            preferred_idx = (len(segments) - 1) // 2

            pipe_annotation_block(link_id, segments, preferred_idx, i, pipe_boundaries, auto_label_post)
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
