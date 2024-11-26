import re
import pandas as pd
import ezdxf
import sys

from Ui_ui import Ui_MainWindow
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator
from PyQt5.QtGui import *
import config
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.MainWindow = Ui_MainWindow()
        self.MainWindow.setupUi(self)
        self.MainWindow.b_browser_inp.clicked.connect(self.loadinp)
        self.MainWindow.b_browser_rpt.clicked.connect(self.loadrpt)
        self.MainWindow.b_reset.clicked.connect(self.reset)
        self.MainWindow.b_draw.clicked.connect(self.draw)
        self.MainWindow.l_block_scale.setText(str(str(config.block_scale)))
        self.MainWindow.l_block_scale.setValidator(QDoubleValidator())
        self.MainWindow.l_joint_scale.setText(str(config.joint_scale))
        self.MainWindow.l_joint_scale.setValidator(QDoubleValidator())
        self.MainWindow.l_text_size.setText(str(config.text_size))
        self.MainWindow.l_text_size.setValidator(QDoubleValidator())
        self.MainWindow.l_leader_distance.setText(str(config.leader_distance))
        self.MainWindow.l_leader_distance.setValidator(QIntValidator())

    def main(self):
        global df_NodeResults, df_LinkResults
        
        # inpFile='test2.inp'
        # rptFile='test2.rpt'

        inpFile=config.inpFile
        rptFile=config.rptFile
        if inpFile != '' and rptFile != '':
            # try:
            rptFile2=self.rptProces(rptFile)
            self.MainWindow.browser_log.append('rpt preprocess finish')

            hr_list=self.multiHr(rptFile2)
            if hr_list==[]:
                multiPattern=False
            else:
                multiPattern=True

            self.readinpdf(inpFile)

            if multiPattern==False: # without patteren
                df_NodeResults=self.readNodeResults('', rptFile2)
                print('NodeResults')
                print(df_NodeResults)

                df_LinkResults=self.readLinkResults('', '', rptFile2)
                print('LinkResults')
                print(df_LinkResults)

                matchLink, matchNode = self.inp_rpt_match()
                if matchLink and matchNode:
                    self.MainWindow.browser_log.append(f'Both input match')
                    self.create_dxf_export()
                else:
                    self.MainWindow.browser_log.append(f'Both input NOT match, please check input files')
                    self.MainWindow.browser_log.append(f'---------------------')

            elif multiPattern==True:   # with patteren
                for hr in hr_list:
                    i=hr_list.index(hr)
                    df_NodeResults=self.readNodeResults(hr, rptFile2)
                    print(f'NodeResults at {hr}')
                    print(df_NodeResults)

                    if i==len(hr_list)-1:
                        df_LinkResults=self.readLinkResults(hr, '', rptFile2)   # with patteren and last hour
                    else:
                        hr2=hr_list[i+1]
                        df_LinkResults=self.readLinkResults(hr, hr2, rptFile2)
                    print(f'LinkResults at {hr}')
                    print(df_LinkResults)

                    matchLink, matchNode = self.inp_rpt_match()
                    if matchLink and matchNode:
                        self.MainWindow.browser_log.append(f'{hr} Both input match')
                        self.create_dxf_export()
                    else:
                        self.MainWindow.browser_log.append(f'{hr} Both input NOT match, please check input files')
                        self.MainWindow.browser_log.append(f'---------------------')

    def create_dxf_export(self, *args, **kwargs):
        global msp

        cad = ezdxf.new()
        msp = cad.modelspace()

        tankerLeaderColor=210
        reservoirLeaderColor=210
        elevLeaderColor=headPressureLeaderColor=210
        demandColor=2

        junctionBlock=cad.blocks.new(name='arrow')
        junctionBlock.add_hatch(color=demandColor).paths.add_polyline_path([(0,0), (30,-50), (-30,-50)], is_closed=True)

        self.createBlocks(cad)
        self.insertBlocks()
        self.drawPipes()
        self.pipeInfo()
        self.demandLeader(demandColor)
        self.elevLeader(elevLeaderColor)
        self.headPressureLeader(headPressureLeaderColor)
        self.reservoirsLeader(reservoirLeaderColor)
        self.tankLeader(tankerLeaderColor)

        # cad.saveas("new_name.dxf")
        savePath, _= QFileDialog.getSaveFileName(self, "儲存", "", filter='dxf (*.dxf)')
        if savePath:
            cad.saveas(savePath)

            self.MainWindow.browser_log.append('.dxf saved')
            self.export(cad)
            self.MainWindow.browser_log.append('All done')
            self.MainWindow.browser_log.append(f'---------------------')
        else:
            self.MainWindow.browser_log.append(f'---------------------')

    def inp_rpt_match(self):
        inputAllLink=pd.concat([df_Pipes['ID'], df_Valves['ID'], df_Pumps['ID']])
        inputAllLink=inputAllLink.sort_values().reset_index(drop=True)
        outputAllLink=df_LinkResults['ID']
        outputAllLink=outputAllLink.sort_values().reset_index(drop=True)

        matchLink=outputAllLink.equals(outputAllLink)

        inputAllNode=pd.concat([df_Junctions['ID'], df_Tanks['ID'], df_Reservoirs['ID']])
        inputAllNode=inputAllNode.sort_values().reset_index(drop=True)
        outputAllNode=df_NodeResults['ID']
        outputAllNode=outputAllNode.sort_values().reset_index(drop=True)

        matchNode=outputAllNode.equals(inputAllNode)
        return matchLink,matchNode

    def readinpdf(self, inpFile):
        global df_Reservoirs, df_Tanks, df_Coords, df_Junctions, df_Pumps, df_Pipes, df_Vertices, df_Valves
        df_Coords=self.readCoords(inpFile)
        print('Coords')
        print(df_Coords)

        df_Junctions=self.readJunctions(inpFile)
        print('Junctions')
        print(df_Junctions)

        df_Reservoirs=self.readReservoirs(inpFile)
        print('Reservoirs')
        print(df_Reservoirs)
            
        df_Tanks=self.readTanks(inpFile)
        print('Tanks')
        print(df_Tanks)

        df_Pumps=self.readPumps(inpFile)
        print('Pumps')
        print(df_Pumps)

        df_Valves=self.readValves(inpFile)
        print('Valves')
        print(df_Valves)

        df_Pipes=self.readPipes(inpFile)
        print('Pipes')
        print(df_Pipes)

        df_Vertices=self.readVertices(inpFile)
        print('Vertices')
        print(df_Vertices)

    def multiHr(self, rptFile2):
        rptFile2_lines=open(rptFile2).readlines()

        i=0
        hr_list=[]
        for l in rptFile2_lines:
            if ' Hrs' in l and i==0:
                h_new=l.split()[3]
                hr_list.append(h_new)
                i+=1
            elif ' Hrs' in l and i>0:
                h_old=h_new
                h_new=l.split()[3]
                if h_new!=h_old:
                    hr_list.append(h_new)
                i+=1

        return hr_list

    def loadinp(self):
        file, type=QFileDialog.getOpenFileName(self, '開啟inp檔',filter='inp (*.inp)')
        self.MainWindow.l_inp_path.setText(file)
        config.inpFile=file

    def loadrpt(self):
        file, type=QFileDialog.getOpenFileName(self, '開啟rpt檔',filter='rpt (*.rpt)')
        self.MainWindow.l_rpt_path.setText(file)
        config.rptFile=file

    def reset(self):
        self.MainWindow.l_block_scale.setText(str(str(config.block_scale)))
        self.MainWindow.l_joint_scale.setText(str(config.joint_scale))
        self.MainWindow.l_text_size.setText(str(config.text_size))
        self.MainWindow.l_leader_distance.setText(str(config.leader_distance))
        
        self.MainWindow.l_inp_path.setText('')
        self.MainWindow.l_rpt_path.setText('')
        config.inpFile=''
        config.rptFile=''

    def draw(self):
        config.block_scale=float(self.MainWindow.l_block_scale.text())
        config.joint_scale=float(self.MainWindow.l_joint_scale.text())
        config.text_size=float(self.MainWindow.l_text_size.text())
        config.leader_distance=float(self.MainWindow.l_leader_distance.text())
        
        self.main()

    def headPressureLeader(self, color):
        from ezdxf.enums import TextEntityAlignment
        try:
            for i in range(0, len(df_Junctions)):
                QCoreApplication.processEvents()
                id=df_Junctions.at[i,'ID']
                x=float(df_Junctions.at[i,'x'])
                y=float(df_Junctions.at[i,'y'])
                result_row=df_NodeResults.index[df_NodeResults['ID']==str(id)].tolist()[0]
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

                leader_up_start_x=x+config.text_size
                leader_up_start_y=y+config.text_size

                leader_up_end_x=leader_up_start_x+config.leader_distance
                leader_up_end_y=leader_up_start_y+config.leader_distance

                msp.add_text(Head, height=config.text_size, dxfattribs={'color': color_head}).set_placement((leader_up_end_x+6*config.text_size,leader_up_end_y+5+2*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
                msp.add_text(Pressure, height=config.text_size, dxfattribs={'color': color_pressure}).set_placement((leader_up_end_x+6*config.text_size,leader_up_end_y+5-1.0*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
                self.MainWindow.browser_log.append(f'Node {id} pressure created')
        except:
            # print(i)
            pass
    
    def createBlocks(self, cad):
        reservoirBlock=cad.blocks.new(name='tank')
        reservoirBlock.add_hatch().paths.add_polyline_path([(100,0), (100,100), (-100,100), (-100,0)], is_closed=True)
        reservoirBlock.add_hatch().paths.add_polyline_path([(50,0), (50,-100), (-50,-100), (-50,0)], is_closed=True)

        tankBlock=cad.blocks.new(name='reservoir')
        tankBlock.add_hatch().paths.add_polyline_path([(100,-50), (100,50), (-100,50), (-100,-50)], is_closed=True)
        tankBlock.add_hatch().paths.add_polyline_path([(100, 50), (100,100), (85,100), (85,50)], is_closed=True)
        tankBlock.add_hatch().paths.add_polyline_path([(-100, 50), (-100,100), (-85,100), (-85,50)], is_closed=True)

        junctionBlock=cad.blocks.new(name='junction')
        junctionBlock.add_hatch().paths.add_edge_path().add_ellipse((0,0), major_axis=(0,50), ratio=1)

        junctionBlock=cad.blocks.new(name='valve')
        junctionBlock.add_hatch().paths.add_polyline_path([(0,0), (50,30), (50,-30)], is_closed=True)
        junctionBlock.add_hatch().paths.add_polyline_path([(0,0), (-50,30), (-50,-30)], is_closed=True)

        from ezdxf.enums import TextEntityAlignment
        from ezdxf.math import Vec2
        pumpBlock=cad.blocks.new(name='pump')
        pumpBlock.add_circle(Vec2(0,0), 100.0)
        pumpBlock.add_text("P", height=100).set_placement((0,0), align=TextEntityAlignment.MIDDLE_CENTER)

    def elevLeader(self, color):
        from ezdxf.enums import TextEntityAlignment

        for i in range(0, len(df_Junctions)):
            QCoreApplication.processEvents()
            id=df_Junctions.at[i,'ID']
            x=float(df_Junctions.at[i,'x'])
            y=float(df_Junctions.at[i,'y'])
            elev=float(df_Junctions.at[i,'Elev'])
            elev=f'{elev:.2f}'

            leader_up_start_x=x+config.text_size
            leader_up_start_y=y+config.text_size

            leader_up_end_x=leader_up_start_x+config.leader_distance
            leader_up_end_y=leader_up_start_y+config.leader_distance

            msp.add_polyline2d([(leader_up_start_x,leader_up_start_y),
                                (leader_up_end_x,leader_up_end_y),
                                (leader_up_end_x+6*config.text_size,leader_up_end_y)], dxfattribs={'color': color})
            msp.add_text(elev, height=config.text_size, dxfattribs={'color': color}).set_placement((leader_up_end_x+6*config.text_size,leader_up_end_y+5+0.5*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            self.MainWindow.browser_log.append(f'Node {id} elev info created')

    def demandLeader(self, color):
        from ezdxf.enums import TextEntityAlignment

        for i in range(0, len(df_Junctions)):
            QCoreApplication.processEvents()
            id=df_Junctions.at[i,'ID']
            x=float(df_Junctions.at[i,'x'])
            y=float(df_Junctions.at[i,'y'])
            demand=df_Junctions.at[i,'Demand']

            if demand != '0':
                leader_down_start_x=x+config.text_size
                leader_down_start_y=y-config.text_size

                leader_down_end_x=leader_down_start_x+config.leader_distance
                leader_down_end_y=leader_down_start_y-config.leader_distance
                
                msp.add_blockref('arrow', [leader_down_end_x,leader_down_end_y], dxfattribs={'xscale':config.block_scale, 'yscale':config.block_scale, 'rotation':225})
                msp.add_polyline2d([(leader_down_start_x,leader_down_start_y),(leader_down_end_x,leader_down_end_y)], dxfattribs={'color': color})
                msp.add_text(demand, height=config.text_size, dxfattribs={'color': color}).set_placement((leader_down_end_x+0.5*config.text_size, leader_down_end_y-0.5*config.text_size), align=TextEntityAlignment.TOP_LEFT)
                self.MainWindow.browser_log.append(f'Node {id} demand info created')

    def reservoirsLeader(self, color):
        from ezdxf.enums import TextEntityAlignment
        for i in range(0, len(df_Reservoirs)):
            QCoreApplication.processEvents()
            id=df_Reservoirs.at[i,'ID']
            x=float(df_Reservoirs.at[i,'x'])
            y=float(df_Reservoirs.at[i,'y'])
            head=float(df_Reservoirs.at[i,'Head'])
            head=f'{head:.2f}'

            leader_up_start_x=x+config.text_size
            leader_up_start_y=y+config.text_size

            leader_up_end_x=leader_up_start_x+config.leader_distance
            leader_up_end_y=leader_up_start_y+config.leader_distance

            msp.add_polyline2d([(leader_up_start_x,leader_up_start_y),
                                (leader_up_end_x,leader_up_end_y),
                                (leader_up_end_x+6*config.text_size,leader_up_end_y)], dxfattribs={'color': color})
            msp.add_text(head, height=config.text_size, dxfattribs={'color': color}).set_placement((leader_up_end_x+6*config.text_size,leader_up_end_y+5+2.0*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msp.add_text('ELEV', height=config.text_size, dxfattribs={'color': color}).set_placement((leader_up_end_x+6*config.text_size,leader_up_end_y+5+0.5*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msp.add_text('Pressure', height=config.text_size, dxfattribs={'color': color}).set_placement((leader_up_end_x+6*config.text_size,leader_up_end_y+5-1.0*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            self.MainWindow.browser_log.append(f'Reservoir {id} info created')

    def tankLeader(self, color):
        from ezdxf.enums import TextEntityAlignment
        for i in range(0, len(df_Tanks)):
            QCoreApplication.processEvents()
            id=df_Tanks.at[i,'ID']
            x=float(df_Tanks.at[i,'x'])
            y=float(df_Tanks.at[i,'y'])

            elev=float(df_Tanks.at[i,'Elev'])
            elev=f'{elev:.2f}'

            minElev=float(df_Tanks.at[i,'MinElev'])
            minElev=f'{minElev:.2f}'

            maxElev=float(df_Tanks.at[i,'MaxElev'])
            maxElev=f'{maxElev:.2f}'

            leader_up_start_x=x+config.text_size
            leader_up_start_y=y+config.text_size

            leader_up_end_x=leader_up_start_x+config.leader_distance
            leader_up_end_y=leader_up_start_y+config.leader_distance

            msp.add_polyline2d([(leader_up_start_x,leader_up_start_y),
                                (leader_up_end_x,leader_up_end_y),
                                (leader_up_end_x+10*config.text_size,leader_up_end_y)], dxfattribs={'color': 210})
            msp.add_text(f'___T', height=config.text_size, dxfattribs={'color': color}).set_placement((leader_up_end_x+10*config.text_size,leader_up_end_y+5+3.5*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msp.add_text(f'Hwl:{maxElev}', height=config.text_size, dxfattribs={'color': color}).set_placement((leader_up_end_x+10*config.text_size,leader_up_end_y+5+2.0*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msp.add_text(f'Mwl:{minElev}', height=config.text_size, dxfattribs={'color': color}).set_placement((leader_up_end_x+10*config.text_size,leader_up_end_y+5+0.5*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msp.add_text(f'Elev:{elev}', height=config.text_size, dxfattribs={'color': color}).set_placement((leader_up_end_x+10*config.text_size,leader_up_end_y+5-1.0*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            self.MainWindow.browser_log.append(f'Tank {id} info created')

    def pipeInfo(self):
        for i in range(0, len(df_Pipes)):
            link_id=df_Pipes.at[i, 'ID']
            if link_id in df_Vertices['LINK'].tolist():
                rows=df_Vertices.index[df_Vertices['LINK']==link_id].tolist()
                if len(rows)==1:   #1個端點
                    start_x=float(df_Pipes.at[i, 'Node1_x'])
                    start_y=float(df_Pipes.at[i, 'Node1_y'])
                    end_x=float(df_Vertices.at[rows[0], 'x'])
                    end_y=float(df_Vertices.at[rows[0], 'y'])
                    self.pipeInfoString(i, start_x, start_y, end_x, end_y)
                    self.flowString(link_id, start_x, start_y, end_x, end_y)
                    pass
                elif len(rows)>=1 and (len(rows) % 2) == 0:   #偶數端點
                    row=len(rows)/2
                    start_x=float(df_Vertices.at[rows[0]+row-1, 'x'])
                    start_y=float(df_Vertices.at[rows[0]+row-1, 'y'])
                    end_x=float(df_Vertices.at[rows[0]+row, 'x'])
                    end_y=float(df_Vertices.at[rows[0]+row, 'y'])
                    self.pipeInfoString(i, start_x, start_y, end_x, end_y)
                    self.flowString(link_id, start_x, start_y, end_x, end_y)
                    pass
                elif len(rows)>=1 and (len(rows) % 2) == 1: #寄數端點
                    row=rows[0]+int(len(rows)/2)
                    start_x=float(df_Vertices.at[row-1, 'x'])
                    start_y=float(df_Vertices.at[row-1, 'y'])
                    end_x=float(df_Vertices.at[row, 'x'])
                    end_y=float(df_Vertices.at[row, 'y'])
                    self.pipeInfoString(i, start_x, start_y, end_x, end_y)
                    self.flowString(link_id, start_x, start_y, end_x, end_y)
            else:   # 無端點
                start_x=float(df_Pipes.at[i, 'Node1_x'])
                start_y=float(df_Pipes.at[i, 'Node1_y'])
                end_x=float(df_Pipes.at[i, 'Node2_x'])
                end_y=float(df_Pipes.at[i, 'Node2_y'])
                self.pipeInfoString(i, start_x, start_y, end_x, end_y)
                self.flowString(link_id, start_x, start_y, end_x, end_y)
                pass

    def pipeInfoString(self, i, start_x, start_y, end_x, end_y):
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
        msp.add_text(text_up, height=config.text_size, rotation=rotation).set_placement((text_x, text_y), align=TextEntityAlignment.BOTTOM_CENTER)

    def flowString(self, id, start_x, start_y, end_x, end_y):
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
        msp.add_text(text_up, height=config.text_size, rotation=rotation).set_placement((text_x, text_y), align=TextEntityAlignment.TOP_CENTER)

    def drawPipes(self):
        for i in range(0, len(df_Pipes)):
            QCoreApplication.processEvents()
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
                self.MainWindow.browser_log.append(f'Pipe {link_id} spline created')
            
            else:
                msp.add_polyline2d([(end_x,end_y), (start_x,start_y)])

    def insertBlocks(self):
        for item in ['tank', 'reservoir', 'junction', 'pump', 'valve']:
            if item == 'tank':
                df=df_Tanks
                for i in range (0, len(df)):
                    QCoreApplication.processEvents()
                    id=df.at[i,'ID']
                    x=float(df.at[i,'x'])
                    y=float(df.at[i,'y'])
                    msp.add_blockref(item, [x,y], dxfattribs={'xscale':config.block_scale, 'yscale':config.block_scale})
                    self.MainWindow.browser_log.append(f'Tank {id} created')

            if item == 'reservoir':
                df=df_Reservoirs
                for i in range (0, len(df)):
                    QCoreApplication.processEvents()
                    id=df.at[i,'ID']
                    x=float(df.at[i,'x'])
                    y=float(df.at[i,'y'])
                    msp.add_blockref(item, [x,y], dxfattribs={'xscale':config.block_scale, 'yscale':config.block_scale})
                    self.MainWindow.browser_log.append(f'Reservoir {id} created')

            if item == 'pump':
                df=df_Pumps
                for i in range (0, len(df)):
                    QCoreApplication.processEvents()
                    id=df.at[i,'ID']
                    x=float(df.at[i,'x'])
                    y=float(df.at[i,'y'])
                    msp.add_blockref(item, [x,y], dxfattribs={'xscale':config.block_scale, 'yscale':config.block_scale})
                    self.MainWindow.browser_log.append(f'Pump {id} created')

            if item == 'valve':
                import math
                df=df_Valves
                for i in range (0, len(df)):
                    QCoreApplication.processEvents()
                    id=df.at[i,'ID']
                    x1=float(df.at[i,'Node1_x'])
                    y1=float(df.at[i,'Node1_y'])
                    x2=float(df.at[i,'Node2_x'])
                    y2=float(df.at[i,'Node2_y'])

                    x=0.5*(float(x1)+float(x2))
                    y=0.5*(float(y1)+float(y2))

                    rotation=math.atan2(y2-y1, x2-x1)
                    rotation=rotation*180/math.pi

                    msp.add_blockref(item, [x,y], dxfattribs={'xscale':config.block_scale, 'yscale':config.block_scale, 'rotation':rotation})
                    msp.add_polyline2d([(x1,y1), (x2,y2)])
                    self.MainWindow.browser_log.append(f'Valve {id} created')

            if item == 'junction':
                df=df_Junctions
                for i in range (0, len(df)):
                    QCoreApplication.processEvents()
                    id=df.at[i,'ID']
                    x=float(df.at[i,'x'])
                    y=float(df.at[i,'y'])
                    msp.add_blockref(item, [x,y], dxfattribs={'xscale':config.joint_scale, 'yscale':config.joint_scale})
                    self.MainWindow.browser_log.append(f'Node {id} created')
                
    def lineStartEnd(self, input, startStr, endStr, start_offset, end_offset):
        index = 0
        with open(input, 'r') as file:
            for line in file:
                index += 1
                if startStr in line:
                    start= index+start_offset
                elif endStr in line:
                    end= index-end_offset
            return start, end

    def line2dict(self, lines, l):
        text=lines[l].replace('\n','')
        text=re.sub(r'\s+', ',', text)
        text=text[:len(text)-1]
        d=text.split(',')
        return d

    def getCoords(self, df):
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

    def readVertices(self, inpFile):
        start, end=self.lineStartEnd(inpFile, '[VERTICES]', '[LABELS]',2,2)
        lines = open(inpFile).readlines()
        df=pd.DataFrame(columns=['LINK','x','y'])
        for l in range (start-1, end):
            d=self.line2dict(lines, l)
            data={
                'LINK':[d[0]],
                'x':[d[1]],
                'y':[d[2]],
                }
            new_df=pd.DataFrame.from_dict(data)
            df=pd.concat([df,new_df])
        df=df.reset_index(drop=True)
        return df

    def readPipes(self, inpFile):
        start, end=self.lineStartEnd(inpFile, '[PIPES]', '[PUMPS]',2,2)
        lines = open(inpFile).readlines()
        df=pd.DataFrame(columns=['ID','Node1','Node2', 'Length', 'Diameter', 'Node1_x', 'Node1_y', 'Node2_x', 'Node2_y'])
        for l in range (start-1, end):
            d=self.line2dict(lines, l)
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

    def readCoords(self, inpFile):
        start, end=self.lineStartEnd(inpFile, '[COORDINATES]', '[VERTICES]',2,2)
        lines = open(inpFile).readlines()
        df=pd.DataFrame(columns=['ID', 'x', 'y'])
        for l in range (start-1, end):
            d=self.line2dict(lines, l)
            data={
                'ID':d[0],
                'x':d[1],
                'y':d[2]
                }
            # new_df=pd.DataFrame.from_dict(data)
            if df.empty:
                df.loc[0]=data
            else:
                df.loc[len(df)]=data
        df=df.reset_index(drop=True)
        return df

    def readJunctions(self, inpFile):
        start, end=self.lineStartEnd(inpFile, '[JUNCTIONS]', '[RESERVOIRS]',2,2)
        lines = open(inpFile).readlines()
        df=pd.DataFrame(columns=['ID', 'Elev', 'Demand', 'x', 'y'])
        for l in range (start-1, end):
            d=self.line2dict(lines, l)
            data={
                'ID':d[1],
                'Elev':d[2],
                'Demand':d[3]
                }
            if df.empty:
                df.loc[0]=data
            else:
                df.loc[len(df)]=data
        df=df.reset_index(drop=True)
        df=self.getCoords(df)
        return df

    def readReservoirs(self, inpFile):
        start, end=self.lineStartEnd(inpFile, '[RESERVOIRS]', '[TANKS]',2,2)
        lines = open(inpFile).readlines()
        df=pd.DataFrame(columns=['ID', 'Head', 'x', 'y'])
        for l in range (start-1, end):
            d=self.line2dict(lines, l)
            data={
                'ID':d[1],
                'Head':d[2]
                }
            if df.empty:
                df.loc[0]=data
            else:
                df.loc[len(df)]=data
        df=df.reset_index(drop=True)
        df=self.getCoords(df)
        return df

    def readTanks(self, inpFile):
        start, end=self.lineStartEnd(inpFile, '[TANKS]', '[PIPES]',2,2)
        lines = open(inpFile).readlines()
        df=pd.DataFrame(columns=['ID', 'Elev', 'MinLevel', 'MaxLevel', 'MinElev', 'MaxElev', 'x', 'y'])
        for l in range (start-1, end):
            d=self.line2dict(lines, l)
            elev=float(d[2])
            MinLevel=float(d[4])
            MaxLevel=float(d[5])
            MinElev=elev+MinLevel
            MaxElev=elev+MaxLevel
            data={
                'ID':d[1],
                'Elev':elev,
                'MinLevel':MinLevel,
                'MaxLevel':MaxLevel,
                'MinElev':MinElev,
                'MaxElev':MaxElev
                }
            if df.empty:
                df.loc[0]=data
            else:
                df.loc[len(df)]=data
        df=df.reset_index(drop=True)
        df=self.getCoords(df)
        return df

    def readValves(self, inpFile):
        start, end=self.lineStartEnd(inpFile, '[VALVES]', '[TAGS]',2,2)
        lines = open(inpFile).readlines()
        df=pd.DataFrame(columns=['ID', 'Node1', 'Node2', 'Node1_x', 'Node1_y', 'Node2_x', 'Node2_y'])
        for l in range (start-1, end):
            d=self.line2dict(lines, l)

            id=d[1]
            Node1=d[2]
            Node2=d[3]
            coords1_row=df_Coords.index[df_Coords['ID']==Node1].tolist()[0]
            coords2_row=df_Coords.index[df_Coords['ID']==Node2].tolist()[0]
            Node1_x=df_Coords.at[coords1_row,'x']
            Node1_y=df_Coords.at[coords1_row,'y']
            Node2_x=df_Coords.at[coords2_row,'x']
            Node2_y=df_Coords.at[coords2_row,'y']

            data={
                'ID':id,
                'Node1':Node1,
                'Node2':Node1,
                'Node1_x':Node1_x,
                'Node1_y':Node1_y,
                'Node2_x':Node2_x,
                'Node2_y':Node2_y,
                }
            if df.empty:
                df.loc[0]=data
            else:
                df.loc[len(df)]=data
        df=df.reset_index(drop=True)
        return df

    def readPumps(self, inpFile):
        start, end=self.lineStartEnd(inpFile, '[PUMPS]', '[VALVES]',2,2)
        lines = open(inpFile).readlines()
        df=pd.DataFrame(columns=['ID', 'Node1', 'Node2', 'Node1_x', 'Node1_y', 'Node2_x', 'Node2_y', 'x', 'y'])
        for l in range (start-1, end):
            d=self.line2dict(lines, l)
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
                'ID':ID,
                'Node1':Node1,
                'Node2':Node2,
                'Node1_x':Node1_x,
                'Node1_y':Node1_y,
                'Node2_x':Node2_x,
                'Node2_y':Node2_y,
                'x':x,
                'y':y
                }
            if df.empty:
                df.loc[0]=data
            else:
                df.loc[len(df)]=data
        df=df.reset_index(drop=True)
        # df=getCoords(df)
        return df

    def readNodeResults(self, hr1, rptFile):
        if hr1=='':
            start_str='Node Results:'
            end_str='Link Results:'
        else:
            start_str=f'Node Results at {hr1} Hrs:'
            end_str=f'Link Results at {hr1} Hrs:'
        start, end=self.lineStartEnd(rptFile, start_str, end_str,5,2)
        lines = open(rptFile).readlines()
        df=pd.DataFrame(columns=['ID', 'Demand', 'Head', 'Pressure'])
        for l in range (start-1, end):
            d=self.line2dict(lines, l)
            # try:
            id=d[1]
            demand=d[2]
            head=d[3]
            pressure=d[4]
            
            data={
                'ID':id,
                'Demand':demand,
                'Head':head,
                'Pressure':pressure,
                }
            if df.empty:
                df.loc[0]=data
            else:
                df.loc[len(df)]=data
            # except:
            #     print(f'error id:{id}')
            #     # break
        df=df.reset_index(drop=True)
        return df

    def readLinkResults(self, hr1, hr2, rptFile):
        if hr1=='':     # without patteren
            start_str='Link Results:'
            end_str='[END]'
        elif hr2=='':    # with patteren and last hour
            start_str=f'Link Results at {hr1} Hrs:'
            end_str='[END]'
        elif hr1!='' and hr2!='':
            start_str=f'Link Results at {hr1} Hrs:'
            end_str=f'Node Results at {hr2} Hrs:'
        start, end=self.lineStartEnd(rptFile, start_str, end_str,5,2)
        lines = open(rptFile).readlines()
        df=pd.DataFrame(columns=['ID', 'Flow', 'Headloss'])
        for l in range (start-1, end):
            d=self.line2dict(lines, l)
            data={
                'ID':d[1],
                'Flow':d[2],
                'Headloss':d[3],
                }
            if df.empty:
                df.loc[0]=data
            else:
                df.loc[len(df)]=data
        df=df.reset_index(drop=True)
        return df

    def rptProces(self, rptPath):
        import os
        from pathlib import Path

        if os.path.exists('temp'):
            pass
        else:
            os.mkdir('temp')
            
        name=Path(rptPath).name
        output=f'temp/{name}'
        if os.path.exists(output):
            os.remove(output)

        with open(rptPath, 'r') as file_in, open(output, 'w') as file_out:
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
                        file_out.write('\n')
                        file_out.write('[END]')
                        break
                    else:
                        file_out.write(lines[i])
                        i+=1
        file_out.close()

        return output

    def export(self, doc):
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
        self.MainWindow.browser_log.append('.svg saved')

        # backend = pymupdf.PyMuPdfBackend()
        # # 3. create the frontend
        # frontend = Frontend(context, backend, config=cfg)
        # # 4. draw the modelspace
        # frontend.draw_layout(msp)
        # # 5. create an A4 page layout
        # page = layout.Page(210, 297, layout.Units.mm, margins=layout.Margins.all(20))
        # # 6. get the PDF rendering as bytes
        # pdf_bytes = backend.get_pdf_bytes(page)
        # with open("pdf_dark_bg.pdf", "wb") as fp:
        #     fp.write(pdf_bytes)
        # self.MainWindow.browser_log.append('.pdf saved')

        # # 6. get the PNG rendering as bytes
        # png_bytes = backend.get_pixmap_bytes(page, fmt="png", dpi=200)
        # with open("png_white_bg.png", "wb") as fp:
        #     fp.write(png_bytes)
        # self.MainWindow.browser_log.append('.png saved')

if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)   # Enable high DPI
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

    # main()