import re
import pandas as pd
import ezdxf
import sys

from Ui_ui import Ui_MainWindow
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

def main():
    global msp, df_Reservoirs, df_Tanks, df_Coords, df_Junctions, df_Pumps, df_Pipes, df_Vertices, df_NodeResults, df_LinkResults
    global text_size, block_scale, leader_distance

    inpFile='test.inp'
    rptFile='test.rpt'
    rptFile2=rptProces(rptFile)

    df_Coords=readCoords(inpFile)
    print('Coords')
    print(df_Coords)

    df_Junctions=readJunctions(inpFile)
    print('Junctions')
    print(df_Junctions)

    df_Reservoirs=readReservoirs(inpFile)
    print('Reservoirs')
    print(df_Reservoirs)
    
    df_Tanks=readTanks(inpFile)
    print('Tanks')
    print(df_Tanks)

    df_Pumps=readPumps(inpFile)
    print('Pumps')
    print(df_Pumps)

    df_Pipes=readPipes(inpFile)
    print('Pipes')
    print(df_Pipes)

    df_Vertices=readVertices(inpFile)
    print('Vertices')
    print(df_Vertices)

    df_NodeResults=readNodeResults(rptFile2)
    print('NodeResults')
    print(df_NodeResults)

    df_LinkResults=readLinkResults(rptFile2)
    print('LinkResults')
    print(df_LinkResults)

    cad = ezdxf.new()
    msp = cad.modelspace()
    block_scale=0.5
    text_size=25
    leader_distance=200

    tankerLeaderColor=210
    reservoirLeaderColor=210
    elevLeaderColor=headPressureLeaderColor=210
    demandColor=2

    junctionBlock=cad.blocks.new(name='arrow')
    junctionBlock.add_hatch(color=demandColor).paths.add_polyline_path([(0,0), (30,-50), (-30,-50)], is_closed=True)

    createBlocks(cad)
    insertBlocks()
    drawPipes()
    pipeInfo()
    demandLeader(demandColor)
    elevLeader(elevLeaderColor)
    headPressureLeader(headPressureLeaderColor)
    reservoirsLeader(reservoirLeaderColor)
    tankLeader(tankerLeaderColor)
    # leaderStyle = cad.mleader_styles.duplicate_entry("Standard", "Leader")
    # leaderStyle.dxf.char_height = text_size
            # ml_builder = msp.add_multileader_mtext("Leader")
        # ml_builder.quick_leader(f'{elev}',
        #                     target=Vec2(x,y),
        #                     segment1=Vec2.from_deg_angle(45, leader_distance),)

    cad.saveas("new_name.dxf")
    export(cad)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.MainWindow = Ui_MainWindow()
        self.MainWindow.setupUi(self)

def headPressureLeader(color):
    for i in range(0, len(df_Junctions)):
        from ezdxf.enums import TextEntityAlignment
        nodeID=df_Junctions.at[i,'ID']
        x=float(df_Junctions.at[i,'x'])
        y=float(df_Junctions.at[i,'y'])
        result_row=df_NodeResults.index[df_NodeResults['ID']==str(nodeID)].tolist()[0]
        Head=df_NodeResults.at[result_row,'Head']
        Pressure=df_NodeResults.at[result_row,'Pressure']

        if float(Pressure)<0:
            color_pressure=1
        else:
            color_pressure=color

        if float(Head)<0:
            color_head=1
        else:
            color_head=color

        leader_up_start_x=x+text_size
        leader_up_start_y=y+text_size

        leader_up_end_x=leader_up_start_x+leader_distance
        leader_up_end_y=leader_up_start_y+leader_distance

        msp.add_text(Head, height=text_size, dxfattribs={'color': color_head}).set_placement((leader_up_end_x+200,leader_up_end_y+5+2*text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
        msp.add_text(Pressure, height=text_size, dxfattribs={'color': color_pressure}).set_placement((leader_up_end_x+200,leader_up_end_y+5-1.0*text_size), align=TextEntityAlignment.MIDDLE_RIGHT)

def createBlocks(cad):
    reservoirBlock=cad.blocks.new(name='tank')
    reservoirBlock.add_hatch().paths.add_polyline_path([(100,0), (100,100), (-100,100), (-100,0)], is_closed=True)
    reservoirBlock.add_hatch().paths.add_polyline_path([(50,0), (50,-100), (-50,-100), (-50,0)], is_closed=True)

    tankBlock=cad.blocks.new(name='reservoir')
    tankBlock.add_hatch().paths.add_polyline_path([(100,-50), (100,50), (-100,50), (-100,-50)], is_closed=True)
    tankBlock.add_hatch().paths.add_polyline_path([(100, 50), (100,100), (85,100), (85,50)], is_closed=True)
    tankBlock.add_hatch().paths.add_polyline_path([(-100, 50), (-100,100), (-85,100), (-85,50)], is_closed=True)

    junctionBlock=cad.blocks.new(name='junction')
    junctionBlock.add_hatch().paths.add_edge_path().add_ellipse((0,0), major_axis=(0,50), ratio=1)

    from ezdxf.enums import TextEntityAlignment
    from ezdxf.math import Vec2
    pumpBlock=cad.blocks.new(name='pump')
    pumpBlock.add_circle(Vec2(0,0), 100.0)
    pumpBlock.add_text("P", height=100).set_placement((0,0), align=TextEntityAlignment.MIDDLE_CENTER)

def elevLeader(color):
    from ezdxf.enums import TextEntityAlignment
    for i in range(0, len(df_Junctions)):
        x=float(df_Junctions.at[i,'x'])
        y=float(df_Junctions.at[i,'y'])
        elev=float(df_Junctions.at[i,'Elev'])
        elev=f'{elev:.2f}'

        leader_up_start_x=x+text_size
        leader_up_start_y=y+text_size

        leader_up_end_x=leader_up_start_x+leader_distance
        leader_up_end_y=leader_up_start_y+leader_distance

        msp.add_polyline2d([(leader_up_start_x,leader_up_start_y),
                            (leader_up_end_x,leader_up_end_y),
                            (leader_up_end_x+200,leader_up_end_y)], dxfattribs={'color': color})
        msp.add_text(elev, height=text_size, dxfattribs={'color': color}).set_placement((leader_up_end_x+200,leader_up_end_y+5+0.5*text_size), align=TextEntityAlignment.MIDDLE_RIGHT)

def demandLeader(color):
    for i in range(0, len(df_Junctions)):
        from ezdxf.math import Vec2
        from ezdxf.enums import TextEntityAlignment
        x=float(df_Junctions.at[i,'x'])
        y=float(df_Junctions.at[i,'y'])
        demand=df_Junctions.at[i,'Demand']

        if demand != '0':
            leader_down_start_x=x+text_size
            leader_down_start_y=y-text_size

            leader_down_end_x=leader_down_start_x+leader_distance
            leader_down_end_y=leader_down_start_y-leader_distance
            
            msp.add_blockref('arrow', [leader_down_end_x,leader_down_end_y], dxfattribs={'xscale':block_scale, 'yscale':block_scale, 'rotation':225})
            msp.add_polyline2d([(leader_down_start_x,leader_down_start_y),(leader_down_end_x,leader_down_end_y)], dxfattribs={'color': color})
            msp.add_text(demand, height=text_size, dxfattribs={'color': color}).set_placement((leader_down_end_x+0.5*text_size, leader_down_end_y-0.5*text_size), align=TextEntityAlignment.TOP_LEFT)

def reservoirsLeader(color):
    from ezdxf.enums import TextEntityAlignment
    for i in range(0, len(df_Reservoirs)):
        x=float(df_Reservoirs.at[i,'x'])
        y=float(df_Reservoirs.at[i,'y'])
        head=float(df_Reservoirs.at[i,'Head'])
        head=f'{head:.2f}'

        leader_up_start_x=x+text_size
        leader_up_start_y=y+text_size

        leader_up_end_x=leader_up_start_x+leader_distance
        leader_up_end_y=leader_up_start_y+leader_distance

        msp.add_polyline2d([(leader_up_start_x,leader_up_start_y),
                            (leader_up_end_x,leader_up_end_y),
                            (leader_up_end_x+200,leader_up_end_y)], dxfattribs={'color': color})
        msp.add_text(head, height=text_size, dxfattribs={'color': color}).set_placement((leader_up_end_x+200,leader_up_end_y+5+2.0*text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
        msp.add_text('ELEV', height=text_size, dxfattribs={'color': color}).set_placement((leader_up_end_x+200,leader_up_end_y+5+0.5*text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
        msp.add_text('Pressure', height=text_size, dxfattribs={'color': color}).set_placement((leader_up_end_x+200,leader_up_end_y+5-1.0*text_size), align=TextEntityAlignment.MIDDLE_RIGHT)

def tankLeader(color):
    from ezdxf.enums import TextEntityAlignment
    for i in range(0, len(df_Tanks)):
        x=float(df_Tanks.at[i,'x'])
        y=float(df_Tanks.at[i,'y'])

        elev=float(df_Tanks.at[i,'Elev'])
        elev=f'{elev:.2f}'

        minElev=float(df_Tanks.at[i,'MinElev'])
        minElev=f'{minElev:.2f}'

        maxElev=float(df_Tanks.at[i,'MaxElev'])
        maxElev=f'{maxElev:.2f}'

        leader_up_start_x=x+text_size
        leader_up_start_y=y+text_size

        leader_up_end_x=leader_up_start_x+leader_distance
        leader_up_end_y=leader_up_start_y+leader_distance

        msp.add_polyline2d([(leader_up_start_x,leader_up_start_y),
                            (leader_up_end_x,leader_up_end_y),
                            (leader_up_end_x+400,leader_up_end_y)], dxfattribs={'color': 210})
        msp.add_text(f'___T', height=text_size, dxfattribs={'color': color}).set_placement((leader_up_end_x+400,leader_up_end_y+5+3.5*text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
        msp.add_text(f'Hwl:{maxElev}', height=text_size, dxfattribs={'color': color}).set_placement((leader_up_end_x+400,leader_up_end_y+5+2.0*text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
        msp.add_text(f'Mwl:{minElev}', height=text_size, dxfattribs={'color': color}).set_placement((leader_up_end_x+400,leader_up_end_y+5+0.5*text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
        msp.add_text(f'Elev:{elev}', height=text_size, dxfattribs={'color': color}).set_placement((leader_up_end_x+400,leader_up_end_y+5-1.0*text_size), align=TextEntityAlignment.MIDDLE_RIGHT)

def pipeInfo():
    for i in range(0, len(df_Pipes)):
        link_id=df_Pipes.at[i, 'ID']
        if link_id in df_Vertices['LINK'].tolist():
            rows=df_Vertices.index[df_Vertices['LINK']==link_id].tolist()
            if len(rows)==1:   #1個端點
                start_x=float(df_Pipes.at[i, 'Node1_x'])
                start_y=float(df_Pipes.at[i, 'Node1_y'])
                end_x=float(df_Vertices.at[rows[0], 'x'])
                end_y=float(df_Vertices.at[rows[0], 'y'])
                pipeInfoString(i, start_x, start_y, end_x, end_y)
                flowString(link_id, start_x, start_y, end_x, end_y)
                pass
            elif len(rows)>=1 and (len(rows) % 2) == 0:   #偶數端點
                row=len(rows)/2
                start_x=float(df_Vertices.at[rows[0]+row-1, 'x'])
                start_y=float(df_Vertices.at[rows[0]+row-1, 'y'])
                end_x=float(df_Vertices.at[rows[0]+row, 'x'])
                end_y=float(df_Vertices.at[rows[0]+row, 'y'])
                pipeInfoString(i, start_x, start_y, end_x, end_y)
                flowString(link_id, start_x, start_y, end_x, end_y)
                pass
            elif len(rows)>=1 and (len(rows) % 2) == 1: #寄數端點
                row=rows[0]+int(len(rows)/2)
                start_x=float(df_Vertices.at[row-1, 'x'])
                start_y=float(df_Vertices.at[row-1, 'y'])
                end_x=float(df_Vertices.at[row, 'x'])
                end_y=float(df_Vertices.at[row, 'y'])
                pipeInfoString(i, start_x, start_y, end_x, end_y)
                flowString(link_id, start_x, start_y, end_x, end_y)
        else:   # 無端點
            start_x=float(df_Pipes.at[i, 'Node1_x'])
            start_y=float(df_Pipes.at[i, 'Node1_y'])
            end_x=float(df_Pipes.at[i, 'Node2_x'])
            end_y=float(df_Pipes.at[i, 'Node2_y'])
            pipeInfoString(i, start_x, start_y, end_x, end_y)
            flowString(link_id, start_x, start_y, end_x, end_y)
            pass

def pipeInfoString(i, start_x, start_y, end_x, end_y):
    import math
    from ezdxf.enums import TextEntityAlignment
    text_x=(start_x+end_x)/2
    text_y=(start_y+end_y)/2
    diameter=df_Pipes.at[i, 'Diameter']
    length=df_Pipes.at[i, 'Length']
    text_up=f'{diameter}-{length}'
    rotation=math.atan2(end_y-start_y, end_x-start_x)
    rotation=rotation*180/math.pi
    if rotation >90 and rotation<180:
        rotation=rotation-180
    elif rotation <-90 and rotation>-180:
        rotation=rotation+180    
    msp.add_text(text_up, height=text_size, rotation=rotation).set_placement((text_x, text_y), align=TextEntityAlignment.BOTTOM_CENTER)

def flowString(id, start_x, start_y, end_x, end_y):
    import math
    from ezdxf.enums import TextEntityAlignment
    text_x=(start_x+end_x)/2
    text_y=(start_y+end_y)/2

    link_row=df_LinkResults.index[df_LinkResults['ID']==id].tolist()[0]

    flow=float(df_LinkResults.at[link_row, 'Flow'])

    if float(flow) >=0:
        dirction='--->'
    else:
        dirction='<---'
        flow=flow*-1

    headloss=df_LinkResults.at[link_row, 'Headloss']
    text_up=f'{flow} ({headloss}) {dirction}'
    rotation=math.atan2(end_y-start_y, end_x-start_x)
    rotation=rotation*180/math.pi
    if rotation >90 and rotation<180:
        rotation=rotation-180
    elif rotation <-90 and rotation>-180:
        rotation=rotation+180    
    msp.add_text(text_up, height=text_size, rotation=rotation).set_placement((text_x, text_y), align=TextEntityAlignment.TOP_CENTER)

def drawPipes():
    for i in range(0, len(df_Pipes)):
        start_x=float(df_Pipes.at[i, 'Node1_x'])
        start_y=float(df_Pipes.at[i, 'Node1_y'])
        end_x=float(df_Pipes.at[i, 'Node2_x'])
        end_y=float(df_Pipes.at[i, 'Node2_y'])

        link_id=df_Pipes.at[i, 'ID']
        if link_id in df_Vertices['LINK'].tolist():
            rows=df_Vertices.index[df_Vertices['LINK']==link_id].tolist()
            firstVert_x=float(df_Vertices.at[rows[0],'x'])
            firstVert_y=float(df_Vertices.at[rows[0],'y'])
            msp.add_polyline2d([(start_x,start_y), (firstVert_x,firstVert_y)])
            for j in rows[:len(rows)-1]:
                x1=float(df_Vertices.at[j,'x'])
                y1=float(df_Vertices.at[j,'y'])
                x2=float(df_Vertices.at[j+1,'x'])
                y2=float(df_Vertices.at[j+1,'y'])
                msp.add_polyline2d([(x1,y1), (x2,y2)])
                pass
        
            lastVert_x=float(df_Vertices.at[rows[len(rows)-1],'x'])
            lastVert_y=float(df_Vertices.at[rows[len(rows)-1],'y'])
            msp.add_polyline2d([(lastVert_x,lastVert_y), (end_x,end_y)])
        
        else:
            msp.add_polyline2d([(end_x,end_y), (start_x,start_y)])

def insertBlocks():
    for item in ['tank', 'reservoir', 'junction', 'pump']:
        if item == 'tank':
            df=df_Tanks
        elif item == 'reservoir':
            df=df_Reservoirs
        elif item == 'junction':
            df=df_Junctions
        elif item == 'pump':
            df=df_Pumps
        for i in range (0, len(df)):
            x=float(df.at[i,'x'])
            y=float(df.at[i,'y'])
            msp.add_blockref(item, [x,y], dxfattribs={'xscale':block_scale, 'yscale':block_scale})

def lineStartEnd(file, startStr, endStr, start_offset, end_offset):
    index = 0
    with open(file, 'r') as file:
        for line in file:
            index += 1
            if startStr in line:
                start= index+start_offset
            elif endStr in line:
                end= index-end_offset
        return start, end

def line2dict(lines, l):
    text=lines[l].replace('\n','')
    text=re.sub(r'\s+', ',', text)
    text=text[:len(text)-1]
    d=text.split(',')
    return d

def getCoords(df):
    '''
    從df_Coords讀取Tank, Reservoir的座標
    '''
    for i in range (0, len(df)):
        ID=df.at[i,'ID']
        row=df_Coords.index[df_Coords['ID']==str(ID)].tolist()[0]
        df.at[i, 'x']=df_Coords.at[row, 'x']
        df.at[i, 'y']=df_Coords.at[row, 'y']
        pass
    return df

def readVertices(inpFile):
    start, end=lineStartEnd(inpFile, '[VERTICES]', '[LABELS]',2,2)
    lines = open(inpFile).readlines()
    df=pd.DataFrame(columns=['LINK','x','y'])
    for l in range (start-1, end):
        d=line2dict(lines, l)
        data={
            'LINK':[d[0]],
            'x':[d[1]],
            'y':[d[2]],
            }
        new_df=pd.DataFrame.from_dict(data)
        df=pd.concat([df,new_df])
    df=df.reset_index(drop=True)
    return df

def readPipes(inpFile):
    start, end=lineStartEnd(inpFile, '[PIPES]', '[PUMPS]',2,2)
    lines = open(inpFile).readlines()
    df=pd.DataFrame(columns=['ID','Node1','Node2', 'Length', 'Diameter', 'Node1_x', 'Node1_y', 'Node2_x', 'Node2_y'])
    for l in range (start-1, end):
        d=line2dict(lines, l)
        data={
            'ID':[d[1]],
            'Node1':[d[2]],
            'Node2':[d[3]],
            'Length':[d[4]],
            'Diameter':[d[5]]
            }
        new_df=pd.DataFrame.from_dict(data)
        df=pd.concat([df,new_df])
    df=df.reset_index(drop=True)

    for i in range (0, len(df)):
        Node1=df.at[i,'Node1']
        row=df_Coords.index[df_Coords['ID']==str(Node1)].tolist()[0]
        df.at[i, 'Node1_x']=df_Coords.at[row, 'x']
        df.at[i, 'Node1_y']=df_Coords.at[row, 'y']

        Node2=df.at[i,'Node2']
        row=df_Coords.index[df_Coords['ID']==str(Node2)].tolist()[0]
        df.at[i, 'Node2_x']=df_Coords.at[row, 'x']
        df.at[i, 'Node2_y']=df_Coords.at[row, 'y']
    return df

def readCoords(inpFile):
    start, end=lineStartEnd(inpFile, '[COORDINATES]', '[VERTICES]',2,2)
    lines = open(inpFile).readlines()
    df=pd.DataFrame(columns=['ID', 'x', 'y'])
    for l in range (start-1, end):
        d=line2dict(lines, l)
        data={
            'ID':[d[0]],
            'x':[d[1]],
            'y':[d[2]]
            }
        new_df=pd.DataFrame.from_dict(data)
        df=pd.concat([df,new_df])
    df=df.reset_index(drop=True)
    return df

def readJunctions(inpFile):
    start, end=lineStartEnd(inpFile, '[JUNCTIONS]', '[RESERVOIRS]',2,2)
    lines = open(inpFile).readlines()
    df=pd.DataFrame(columns=['ID', 'Elev', 'Demand', 'x', 'y'])
    for l in range (start-1, end):
        d=line2dict(lines, l)
        data={
            'ID':[d[1]],
            'Elev':[d[2]],
            'Demand':[d[3]]
            }
        new_df=pd.DataFrame.from_dict(data)
        df=pd.concat([df,new_df])
    df=df.reset_index(drop=True)
    df=getCoords(df)
    return df

def readReservoirs(inpFile):
    start, end=lineStartEnd(inpFile, '[RESERVOIRS]', '[TANKS]',2,2)
    lines = open(inpFile).readlines()
    df=pd.DataFrame(columns=['ID', 'Head', 'x', 'y'])
    for l in range (start-1, end):
        d=line2dict(lines, l)
        data={
            'ID':[d[1]],
            'Head':[d[2]]
            }
        new_df=pd.DataFrame.from_dict(data)
        df=pd.concat([df,new_df])
    df=df.reset_index(drop=True)
    df=getCoords(df)
    return df

def readTanks(inpFile):
    start, end=lineStartEnd(inpFile, '[TANKS]', '[PIPES]',2,2)
    lines = open(inpFile).readlines()
    df=pd.DataFrame(columns=['ID', 'Elev', 'MinLevel', 'MaxLevel', 'x', 'y'])
    for l in range (start-1, end):
        d=line2dict(lines, l)
        elev=float(d[2])
        MinLevel=float(d[4])
        MaxLevel=float(d[5])
        MinElev=elev+MinLevel
        MaxElev=elev+MaxLevel
        data={
            'ID':[d[1]],
            'Elev':[elev],
            'MinLevel':[MinLevel],
            'MaxLevel':[MaxLevel],
            'MinElev':[MinElev],
            'MaxElev':[MaxElev]
            }
        new_df=pd.DataFrame.from_dict(data)
        df=pd.concat([df,new_df])
    df=df.reset_index(drop=True)
    df=getCoords(df)
    return df

def readPumps(inpFile):
    start, end=lineStartEnd(inpFile, '[PUMPS]', '[VALVES]',2,2)
    lines = open(inpFile).readlines()
    df=pd.DataFrame(columns=['ID', 'Node1', 'Node2', 'Node1_x', 'Node1_y', 'Node2_x', 'Node2_y', 'x', 'y'])
    for l in range (start-1, end):
        d=line2dict(lines, l)
        ID=[d[1]][0]
        Node1=[d[2]][0]
        Node2=[d[3]][0]
        coords1_row=df_Coords.index[df_Coords['ID']==Node1].tolist()[0]
        coords2_row=df_Coords.index[df_Coords['ID']==Node2].tolist()[0]
        Node1_x=df_Coords.at[coords1_row,'x']
        Node1_y=df_Coords.at[coords1_row,'y']
        Node2_x=df_Coords.at[coords2_row,'x']
        Node2_y=df_Coords.at[coords2_row,'y']
        x=0.5*(float(Node1_x)+float(Node2_x))
        y=0.5*(float(Node1_y)+float(Node2_y))
        data={
            'ID':[ID],
            'Node1':[Node1],
            'Node2':[Node2],
            'Node1_x':[Node1_x],
            'Node1_y':[Node1_y],
            'Node2_x':[Node2_x],
            'Node2_y':[Node2_y],
            'x':[x],
            'y':[y]
            }
        new_df=pd.DataFrame.from_dict(data)
        df=pd.concat([df,new_df])
    df=df.reset_index(drop=True)
    # df=getCoords(df)
    return df

def readNodeResults(rptFile):
    start, end=lineStartEnd(rptFile, 'Node Results:', 'Link Results:',5,2)
    lines = open(rptFile).readlines()
    df=pd.DataFrame(columns=['ID', 'Demand', 'Head', 'Pressure'])
    for l in range (start-1, end):
        d=line2dict(lines, l)
        try:
            data={
                'ID':[d[1]],
                'Demand':[d[2]],
                'Head':[d[3]],
                'Pressure':[d[4]],
                }
            new_df=pd.DataFrame.from_dict(data)
            df=pd.concat([df,new_df])
        except:
            break
    df=df.reset_index(drop=True)
    return df

def readLinkResults(rptFile):
    start, end=lineStartEnd(rptFile, 'Link Results:', '[END]',5,1)
    lines = open(rptFile).readlines()
    df=pd.DataFrame(columns=['ID', 'Flow', 'Headloss'])
    for l in range (start-1, end):
        d=line2dict(lines, l)
        data={
            'ID':[d[1]],
            'Flow':[d[2]],
            'Headloss':[d[3]],
            }
        new_df=pd.DataFrame.from_dict(data)
        df=pd.concat([df,new_df])
    df=df.reset_index(drop=True)
    return df

def rptProces(rptInputFile):
    import os

    output=f'temp/{rptInputFile}'
    if os.path.exists(output):
        os.remove(output)

    with open(rptInputFile, 'r') as file_in, open(output, 'w') as file_out:
        lines=file_in.readlines()
        i=0
        while i < len(lines):
            if '\x0c\n' in lines[i]:
                i+=1
                continue

            elif 'Page' in lines[i]:
                i+=1
                continue
                
            elif '\n' == lines[i]:
                i+=1
                continue

            elif 'continued' in lines[i]:
                i+=5
                continue
            else:
                if i == len(lines)-1:
                    file_out.write('[END]')
                    break
                else:
                    file_out.write(lines[i])
                    i+=1
    file_out.close()

    return output


def export(doc):
    from ezdxf.addons.drawing import Frontend, RenderContext, svg, layout, config, pymupdf
    msp = doc.modelspace()
    context = RenderContext(doc)
    backend = svg.SVGBackend()
    cfg = config.Configuration(
        background_policy=config.BackgroundPolicy.WHITE,
    )
    frontend = Frontend(context, backend, config=cfg)
    frontend.draw_layout(msp)
    page = layout.Page(0, 0, layout.Units.mm, margins=layout.Margins.all(2))
    svg_string = backend.get_string(
        page, settings=layout.Settings(scale=1, fit_page=False)
    )
    with open("output.svg", "wt", encoding="utf8") as fp:
        fp.write(svg_string)


    backend = pymupdf.PyMuPdfBackend()
    # 3. create the frontend
    frontend = Frontend(context, backend, config=cfg)
    # 4. draw the modelspace
    frontend.draw_layout(msp)
    # 5. create an A4 page layout
    page = layout.Page(210, 297, layout.Units.mm, margins=layout.Margins.all(20))
    # 6. get the PDF rendering as bytes
    pdf_bytes = backend.get_pdf_bytes(page)
    with open("pdf_dark_bg.pdf", "wb") as fp:
        fp.write(pdf_bytes)

    # 6. get the PNG rendering as bytes
    png_bytes = backend.get_pixmap_bytes(page, fmt="png", dpi=200)
    with open("png_white_bg.png", "wb") as fp:
        fp.write(png_bytes)

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)   # Enable high DPI
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())