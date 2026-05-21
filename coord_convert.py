import os
import re

from pyproj import Transformer

_T_Z1 = Transformer.from_crs(4326, 3826, always_xy=True)  # WGS84 → TWD97 TM2 CM=121°
_T_Z2 = Transformer.from_crs(4326, 3825, always_xy=True)  # WGS84 → TWD97 TM2 CM=119°


def wgs84_to_twd97_tm2(lon_deg, lat_deg):
    """Convert WGS84 (lon, lat degrees) to TWD97 TM2 (easting, northing metres)."""
    t = _T_Z1 if lon_deg >= 120.0 else _T_Z2
    return t.transform(lon_deg, lat_deg)


def convert_df_wgs84_to_twd97(df):
    """Convert x,y columns of a dataframe (with 'x' and 'y' columns) from WGS84 to TWD97 TM2.

    Raises ValueError if any coordinate is outside geographic range (|x|>180 or |y|>90).
    Returns a new dataframe with converted coordinates.
    """
    df = df.copy()
    xs = df['x'].astype(float).tolist()
    ys = df['y'].astype(float).tolist()
    for x, y in zip(xs, ys):
        if abs(x) > 180.0 or abs(y) > 90.0:
            raise ValueError(
                f'座標 ({x}, {y}) 不像 WGS84 地理座標（值超出 ±180/±90），請確認座標系統'
            )
    en = [wgs84_to_twd97_tm2(x, y) for x, y in zip(xs, ys)]
    df['x'] = [e for e, n in en]
    df['y'] = [n for e, n in en]
    return df


def convert_inp_wgs84_to_twd97(inp_path):
    """
    Read an EPANET INP file, convert [COORDINATES] and [VERTICES] from WGS84 to TWD97 TM2,
    and save as '<original_name>_TWD97.inp' in the same directory.

    Returns (new_file_path, converted_point_count).
    Raises ValueError if no convertible coordinates are found or coordinates are not geographic.
    """
    out_path = os.path.splitext(inp_path)[0] + '_TWD97.inp'

    with open(inp_path, 'r', errors='ignore') as f:
        lines = f.readlines()

    in_coords = False
    in_vertices = False
    converted_count = 0
    out_lines = []

    for line in lines:
        stripped = line.strip()

        if re.match(r'^\[COORDINATES\]', stripped, re.IGNORECASE):
            in_coords, in_vertices = True, False
            out_lines.append(line)
            continue
        elif re.match(r'^\[VERTICES\]', stripped, re.IGNORECASE):
            in_vertices, in_coords = True, False
            out_lines.append(line)
            continue
        elif re.match(r'^\[', stripped):
            in_coords = in_vertices = False
            out_lines.append(line)
            continue

        if (in_coords or in_vertices) and stripped and not stripped.startswith(';'):
            parts = stripped.split()
            if len(parts) >= 3:
                try:
                    x, y = float(parts[1]), float(parts[2])
                    if abs(x) > 180.0 or abs(y) > 90.0:
                        raise ValueError(
                            f'座標 ({x}, {y}) 不像 WGS84 地理座標（值超出 ±180/±90），請確認座標系統'
                        )
                    e, n = wgs84_to_twd97_tm2(x, y)
                    out_lines.append(f'{parts[0]:<16}\t{e:.3f}\t{n:.3f}\n')
                    converted_count += 1
                    continue
                except ValueError:
                    raise
                except Exception:
                    pass

        out_lines.append(line)

    if converted_count == 0:
        raise ValueError('找不到可轉換的 WGS84 座標，請確認 INP 檔座標系統')

    with open(out_path, 'w', encoding='utf-8', errors='ignore') as f:
        f.writelines(out_lines)

    return out_path, converted_count
