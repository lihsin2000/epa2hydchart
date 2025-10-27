
import pandas as pd
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from main import MainWindow
    from ezdxf.document import Drawing
    from ezdxf.layouts import Modelspace

# main window instance
main_window: Optional['MainWindow'] = None

# default
block_size = None
joint_size = None
text_size = None
leader_distance = None
line_width = None

BLOCK_SIZE_DEFAULT = 25.0
JOINT_SIZE_DEFAULT = 25.0
TEXT_SIZE_DEFAULT = 25.0
LEADER_DISTANCE_DEFAULT = 25.0
LINE_WIDTH_DEFAULT = 1

inp_file = None
rpt_file = None
output_folder = None
proj_name = None

hr_list = []
df_node_results: pd.DataFrame = pd.DataFrame()
df_link_results: pd.DataFrame = pd.DataFrame()

arranged_rpt_file_path = None
df_coords: Optional[pd.DataFrame] = None
df_junctions: Optional[pd.DataFrame] = None
df_reservoirs: Optional[pd.DataFrame] = None
df_tanks: Optional[pd.DataFrame] = None
df_pumps: Optional[pd.DataFrame] = None
df_valves: Optional[pd.DataFrame] = None
df_pipes: Optional[pd.DataFrame] = None
df_vertices: Optional[pd.DataFrame] = None

cad: Optional['Drawing'] = None
msp: Optional['Modelspace'] = None
dxf_path = None

digit_decimal = None

export_dxf_success = None
export_svg_success = None
export_png_success = None

UNIT_HEADLOSS_THRESHOLD = 1.0
UNIT_VELOCITY_THRESHOLD = 0.3
NAGAVITE_PRESSURE_THRESHOLD = 0.0
LOW_PRESSURE_THRESHOLD = 10.0

any_error = False

progress_steps = None
progress_value = None
progress_space = None
