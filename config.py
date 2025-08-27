
import pandas as pd
# default
block_size=None
joint_size=None
text_size=None
leader_distance=None
line_width=None

block_size_default=100.0
joint_size_default=25.0
text_size_default=25.0
leader_distance_default=50.0
line_with_default=0

inpFile=None
rptFile=None
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