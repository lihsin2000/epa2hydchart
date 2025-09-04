
import pandas as pd
# default
block_size=None
joint_size=None
text_size=None
leader_distance=None
line_width=None

BLOCK_SIZE_DEFAULT=100.0
JOINT_SIZE_DEFAULT=25.0
TEXT_SIZE_DEFAULT=25.0
LEADER_DISTANCE_DEFAULT=50.0
LINE_WIDTH_DEFAULT=0

inpFile=None
rptFile=None
output_folder=None
projName=None

hr_list=[]
df_NodeResults=pd.DataFrame()
df_LinkResults=pd.DataFrame()

arranged_rpt_file_path=None 
df_Coords=None
df_Junctions=None
df_Reservoirs=None
df_Tanks=None
df_Pumps=None
df_Valves=None
df_Pipes=None
df_Vertices=None

cad=None
msp=None
dxfPath=None

digit_decimal=None

export_dxf_success=None
export_svg_success=None
export_png_success=None

UNIT_HEADLOSS_THRESHOLD=1.0
UNIT_VELOCITY_THRESHOLD=0.3
NAGAVITE_PRESSURE_THRESHOLD=0.0
LOW_PRESSURE_THRESHOLD=10.0