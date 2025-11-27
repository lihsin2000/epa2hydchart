import math


def get_rectangle_corners(cx, cy, w, h, angle_deg):
    """
    Get 4 corners of a rotated rectangle.

    Parameters
    ----------
    cx : float
        Center x-coordinate.
    cy : float
        Center y-coordinate.
    w : float
        Width of the rectangle.
    h : float
        Height of the rectangle.
    angle_deg : float
        Rotation angle in degrees.

    Returns
    -------
    list of tuples
        List of (x, y) coordinates for the 4 corners.
    """
    angle = math.radians(angle_deg)
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    # Rectangle corners relative to center
    dx = w / 2
    dy = h / 2
    corners = [
        (cx - dx*cos_a + dy*sin_a, cy - dx*sin_a - dy*cos_a),  # top-left
        (cx + dx*cos_a + dy*sin_a, cy + dx*sin_a - dy*cos_a),  # top-right
        (cx + dx*cos_a - dy*sin_a, cy + dx*sin_a + dy*cos_a),  # bottom-right
        (cx - dx*cos_a - dy*sin_a, cy - dx*sin_a + dy*cos_a),  # bottom-left
    ]
    return corners


def project_polygon(axis, corners):
    """
    Project a polygon onto an axis, return (min, max) of projection.

    Parameters
    ----------
    axis : tuple of float
        Normalized axis vector (x, y).
    corners : list of tuples
        List of (x, y) coordinates of the polygon's corners.

    Returns
    -------
    tuple of float
        (min projection, max projection) on the axis.
    """
    dots = [corner[0]*axis[0] + corner[1]*axis[1] for corner in corners]
    return min(dots), max(dots)


def overlap_on_axis(axis, corners1, corners2):
    """
    Check if projections overlap on this axis.

    Parameters
    ----------
    axis : tuple of float
        Normalized axis vector (x, y).
    corners1 : list of tuples
        List of (x, y) coordinates of the first polygon's corners.
    corners2 : list of tuples
        List of (x, y) coordinates of the second polygon's corners.

    Returns
    -------
    bool
        True if projections overlap, False otherwise.
    """
    min1, max1 = project_polygon(axis, corners1)
    min2, max2 = project_polygon(axis, corners2)
    return not (max1 < min2 or max2 < min1)


def rectangles_overlap(rect1, rect2):
    """
    Check if two rectangles overlap using Separating Axis Theorem.

    Parameters
    ----------
    rect1 : tuple of float
        Rectangle 1 parameters (cx, cy, w, h, angle_deg).
    rect2 : tuple of float
        Rectangle 2 parameters (cx, cy, w, h, angle_deg).

    Returns
    -------
    bool
        True if rectangles overlap, False otherwise.
    """
    corners1 = get_rectangle_corners(*rect1)
    corners2 = get_rectangle_corners(*rect2)

    # Compute edges for both rectangles
    edges = []
    for corners in (corners1, corners2):
        for i in range(4):
            p1 = corners[i]
            p2 = corners[(i + 1) % 4]
            edge = (p2[0] - p1[0], p2[1] - p1[1])
            # perpendicular (normal) to the edge
            axis = (-edge[1], edge[0])
            # normalize axis
            length = math.hypot(axis[0], axis[1])
            axis = (axis[0]/length, axis[1]/length)
            edges.append(axis)

    # Check all axes (SAT)
    for axis in edges:
        if not overlap_on_axis(axis, corners1, corners2):
            return False  # Separating axis found → no overlap
    return True  # No separating axis → overlap


# --- Example usage ---
rect1 = (0, 0, 4, 2, 0)       # Rectangle centered at (0,0), no rotation
rect2 = (2, 0, 4, 2, 30)      # Rectangle centered at (2,0), rotated 30°

# print("Overlap:", rectangles_overlap(rect1, rect2))
