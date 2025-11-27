
from typing import TYPE_CHECKING, Optional
import logging

if TYPE_CHECKING:
    from main import MainWindow
    from ezdxf.document import Drawing
    from ezdxf.layouts import Modelspace
    import pandas as pd

# Global logger
logger = logging.getLogger('epa2hydchart')

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

HEADLOSS_THRESHOLD_DEFAULT = 1.0
VELOCITY_THRESHOLD_DEFAULT = 0.3
PRESSURE_THRESHOLD_DEFAULT = 10.0

inp_file = None
rpt_file = None
output_folder = None
proj_name = None

hr_list = []
df_node_results = None  # Will be initialized as pd.DataFrame when needed
df_link_results = None  # Will be initialized as pd.DataFrame when needed

arranged_rpt_file_path = None
df_coords = None  # Optional[pd.DataFrame]
df_junctions = None  # Optional[pd.DataFrame]
df_reservoirs = None  # Optional[pd.DataFrame]
df_tanks = None  # Optional[pd.DataFrame]
df_pump_curves = None  # Optional[pd.DataFrame]
df_pumps = None  # Optional[pd.DataFrame]
df_valves = None  # Optional[pd.DataFrame]
df_pipes = None  # Optional[pd.DataFrame]
df_vertices = None  # Optional[pd.DataFrame]

cad: Optional['Drawing'] = None
msp: Optional['Modelspace'] = None
dxf_path = None

digit_decimal = None

export_dxf_success = None
export_svg_success = None
export_png_success = None

unit_headloss_threshold = 1.0
unit_velocity_threshold = 0.3
nagaive_pressure_threshold = 0.0
low_pressure_threshold = 10.0

any_error = False

progress_steps = None
progress_value = None
progress_space = None
