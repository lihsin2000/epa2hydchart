
import pandas as pd
# default
block_scale=100
joint_scale=25
text_size=25.0
leader_distance=50.0

block_scale_default=100.0
joint_scale_default=25.0
text_size_default=25.0
leader_distance_default=50.0

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