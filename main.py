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
        self.MainWindow.b_draw.clicked.connect(self.proceed)
        self.MainWindow.l_block_scale.setText(str(config.block_scale))
        self.MainWindow.l_block_scale.setValidator(QDoubleValidator())
        self.MainWindow.l_joint_scale.setText(str(config.joint_scale))
        self.MainWindow.l_joint_scale.setValidator(QDoubleValidator())
        self.MainWindow.l_text_size.setText(str(config.text_size))
        self.MainWindow.l_text_size.setValidator(QDoubleValidator())
        self.MainWindow.l_leader_distance.setText(str(config.leader_distance))
        self.MainWindow.l_leader_distance.setValidator(QIntValidator())

    def main(self):
        global df_NodeResults, df_LinkResults
        QCoreApplication.processEvents()

        inpFile=config.inpFile
        rptFile=config.rptFile

        import os
        if inpFile and rptFile:

            dxfPath, _= QFileDialog.getSaveFileName(self, "儲存", "", filter='dxf (*.dxf)')
            file_name = os.path.basename(dxfPath)
            
            self.inp_to_df(inpFile)

            if hr_list==[]: # 單一時間結果
                try:
                    df_NodeResults=self.readNodeResults(hr=None, input=rptFile2)
                    df_LinkResults=self.readLinkResults(hr1=None, input=rptFile2)
                    matchLink, matchNode = self.inp_rpt_match()
                    self.process2(matchLink=matchLink, matchNode=matchNode, dxfPath=dxfPath, hr='')
                except Exception as e:
                    print(e)
                    self.MainWindow.browser_log.append(f'[Error]不明錯誤，中止匯出')
                    self.MainWindow.browser_log.append(f'---------------------')
            else:   # 多時段結果
                hr_list_select=[]
                items=self.MainWindow.list_hrs.selectedItems()
                for item in items:
                    hr_list_select.append(item.text())
                
                for h in hr_list_select:
                    try:
                        df_NodeResults=self.readNodeResults(hr=h, input=rptFile2)
                        i_hr1=hr_list.index(h)
                        i_hr2=i_hr1+1

                        if 1<=i_hr2<=len(hr_list)-1:
                            hr2=hr_list[i_hr2]
                            df_LinkResults=self.readLinkResults(hr1=h, hr2=hr2, input=rptFile2)
                        elif i_hr2==len(hr_list):
                            df_LinkResults=self.readLinkResults(hr1=h, hr2='', input=rptFile2)
                        else:
                            self.MainWindow.browser_log.append(f'[Error]不明錯誤，中止匯出')
                            self.MainWindow.browser_log.append(f'---------------------')
                            break
                        
                        matchLink, matchNode = self.inp_rpt_match()
                        self.process2(matchLink=matchLink, matchNode=matchNode, dxfPath=dxfPath, hr=h)

                    except Exception as e:
                        print(e)
                        self.MainWindow.browser_log.append(f'[Error]不明錯誤，中止匯出')
                        self.MainWindow.browser_log.append(f'---------------------')
                        break

    def process2(self, *args, **kwargs):
        import os
        matchLink=kwargs.get('matchLink')
        matchNode=kwargs.get('matchNode')
        dxfPath=kwargs.get('dxfPath')
        h=kwargs.get('hr')

        if h=='':
            hr_str=''
        else:
            hr_str=h

        dictionary=os.path.dirname(dxfPath)
        file=os.path.splitext(os.path.basename(dxfPath))[0]

        if matchLink and matchNode:
            self.MainWindow.browser_log.append(f'{hr_str} .rpt及.inp內容相符')
            cad, msp=self.create_modelspace()

            tankerLeaderColor=210
            reservoirLeaderColor=210
            elevLeaderColor=headPressureLeaderColor=pumpAnnotaionColor=valveAnnotaionColor=210
            demandColor=74

            arrowBlock=cad.blocks.new(name='arrow')
            arrowBlock.add_polyline2d([(0,0), (30,-50), (-30,-50)], close=True,dxfattribs={'color': demandColor})
            arrowBlock.add_hatch(color=demandColor).paths.add_polyline_path([(0,0), (30,-50), (-30,-50)], is_closed=True)

            self.createBlocks(cad)
            self.insertBlocks()
            self.drawPipes()
            self.pipeInfo()
            self.demandLeader(demandColor)
            self.elevLeader(elevLeaderColor)
            self.headPressureLeader(headPressureLeaderColor)
            self.reservoirsLeader(reservoirLeaderColor)
            self.tankLeader(tankerLeaderColor)
            self.pumpAnnotation(pumpAnnotaionColor)
            self.valveAnnotation(valveAnnotaionColor)
            self.addTitle(hr_str=hr_str)

            if dxfPath:
                hr_str=hr_str.replace(':','-')
                if len(hr_list)>=2:
                    dxfPath=f'{dictionary}/{file}_{hr_str}.dxf'

                self.save_dxf(cad=cad, path=dxfPath)
                self.MainWindow.browser_log.append(f'{h} .dxf 已存檔')

                svg_path=dxfPath.replace('.dxf', '.svg')
                self.save_svg(msp=msp, cad=cad, path=svg_path)
                self.MainWindow.browser_log.append(f'{h} .svg 已存檔')

                png_path=dxfPath.replace('.dxf', '.png')
                self.save_png(msp=msp, cad=cad, pngPath=png_path, svgPath=svg_path)
                self.MainWindow.browser_log.append(f'{h} .png 已存檔')

                self.MainWindow.browser_log.append('完成!')
                self.MainWindow.browser_log.append(f'---------------------')
            
        else:
            self.MainWindow.browser_log.append(f'[Error]{h}.rpt及.inp內容不符，中止匯出')
            self.MainWindow.browser_log.append(f'---------------------')

    def create_modelspace(self, *args, **kwargs):
        global msp

        cad = ezdxf.new()
        msp = cad.modelspace()
        cad.styles.new("epa2HydChart", dxfattribs={"font" : "Microsoft JhengHei"})

        return cad, msp

    def addTitle(self, *args, **kwargs):
        hr=kwargs.get('hr_str')

        # 計算左上角座標
        xs=df_Coords['x'].tolist()+df_Vertices['x'].tolist()
        x_min=min(xs)

        ys=df_Coords['y'].tolist()+df_Vertices['y'].tolist()
        y_max=max(ys)

        projName=self.MainWindow.l_projName.text()

        # 計算Q值
        from decimal import Decimal
        Q=0
        for i in range(0, len(df_Junctions)):
            id=df_Junctions.at[i,'ID']
            row=df_NodeResults.index[df_NodeResults['ID']==id].tolist()[0]
            if df_NodeResults.at[row, 'Demand'] != None:
                Q=Q+Decimal(df_NodeResults.at[row, 'Demand'])
            else:
                self.MainWindow.browser_log.append(f'[Error]節點 {id} Demand數值錯誤，Q值總計可能有誤')

        # 匯整C值
        C_str=''
        Cs=df_Pipes['Roughness'].unique()
        for c in Cs:
            C_str=C_str+f'{c},'
        C_str=C_str[:len(C_str)-1]

        # 加入文字
        from ezdxf.enums import TextEntityAlignment
        msp.add_text(projName, height=2*config.text_size, dxfattribs={"style": "epa2HydChart"}).set_placement((x_min,y_max+16*config.text_size), align=TextEntityAlignment.TOP_LEFT)
        
        if hr=='':
            msp.add_text(f'Q={Q} CMD', height=2*config.text_size, dxfattribs={"style": "epa2HydChart"}).set_placement((x_min,y_max+13*config.text_size), align=TextEntityAlignment.TOP_LEFT)
        else:
            msp.add_text(f'{hr} Q={Q} CMD', height=2*config.text_size, dxfattribs={"style": "epa2HydChart"}).set_placement((x_min,y_max+13*config.text_size), align=TextEntityAlignment.TOP_LEFT)
        
        msp.add_text(f'C={C_str}', height=2*config.text_size, dxfattribs={"style": "epa2HydChart"}).set_placement((x_min,y_max+10*config.text_size), align=TextEntityAlignment.TOP_LEFT)

    def save_dxf(self, *args, **kwargs):
        cad=kwargs.get('cad')
        dxfPath=kwargs.get('path')
        if dxfPath:
            while True:
                try:
                    cad.saveas(dxfPath)
                    break
                except:
                    from PyQt5.QtWidgets import (QApplication, QMessageBox)
                    msg_box = QMessageBox(self)
                    msg_box.setIcon(QMessageBox.Critical)
                    msg_box.setWindowTitle("錯誤")
                    msg_box.setText(f'{dxfPath}無法儲存')
                    retry_button = msg_box.addButton("重試", QMessageBox.ActionRole)
                    msg_box.exec()
                    if msg_box.clickedButton() == retry_button:
                        continue

    def save_png(self, *args, **kwargs):
        msp=kwargs.get('msp')
        cad=kwargs.get('cad')
        pngPath=kwargs.get('pngPath')
        svgPath=kwargs.get('svgPath')

        import cairosvg
        # lib: GTK+ for Windows Runtime Environment Installer
        # https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
        # https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer/releases/download/2022-01-04/gtk3-runtime-3.24.31-2022-01-04-ts-win64.exe

        cairosvg.svg2png(
            url=svgPath,
            write_to=pngPath,
            output_width=10000,
            dpi=600
            )

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

    def inp_to_df(self, inpFile):
        global df_Reservoirs, df_Tanks, df_Coords, df_Junctions, df_Pumps, df_Pipes, df_Vertices, df_Valves
        df_Coords=self.readCoords(inpFile)
        # print('Coords')
        # print(df_Coords)

        df_Junctions=self.readJunctions(inpFile)
        # print('Junctions')
        # print(df_Junctions)

        df_Reservoirs=self.readReservoirs(inpFile)
        # print('Reservoirs')
        # print(df_Reservoirs)
            
        df_Tanks=self.readTanks(inpFile)
        # print('Tanks')
        # print(df_Tanks)

        df_Pumps=self.readPumps(inpFile)
        # print('Pumps')
        # print(df_Pumps)

        df_Valves=self.readValves(inpFile)
        # print('Valves')
        # print(df_Valves)

        df_Pipes=self.readPipes(inpFile)
        # print('Pipes')
        # print(df_Pipes)

        df_Vertices=self.readVertices(inpFile)
        # print('Vertices')
        # print(df_Vertices)
        pass

    def multiHr(self, rptFile2):
        global hr_list
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
        import os
        
        file, type=QFileDialog.getOpenFileName(self, '開啟inp檔',filter='inp (*.inp)')
        if self.MainWindow.l_inp_path.text() =='':
            self.MainWindow.l_inp_path.setText(file)
        elif self.MainWindow.l_inp_path.text() !='' and file=='':
            file=self.MainWindow.l_inp_path.text()
        else:
            self.MainWindow.l_inp_path.setText(file)
        config.inpFile=file

        config.projName=os.path.splitext(os.path.basename(file))[0]
        self.MainWindow.l_projName.setText(config.projName)

    def loadrpt(self):
        global rptFile2
        file, type=QFileDialog.getOpenFileName(self, '開啟rpt檔',filter='rpt (*.rpt)')

        if self.MainWindow.l_rpt_path.text() !='' and file=='':
            file=self.MainWindow.l_rpt_path.text()
        else:
            self.MainWindow.list_hrs.clear()
            self.MainWindow.l_rpt_path.setText(file)

            rptFile2=self.rptProces(file)
            self.MainWindow.browser_log.append('.rpt前處理完成')

            hr_list=self.multiHr(rptFile2)

            if hr_list==[]:
                hr_list=['']
                self.MainWindow.list_hrs.addItems(['單一時段'])
                self.MainWindow.list_hrs.selectAll()
            else:
                self.MainWindow.list_hrs.addItems(hr_list)
                self.MainWindow.list_hrs.selectAll()

        config.rptFile=file

    def reset(self):
        self.MainWindow.l_block_scale.setText(str(config.block_scale_default))
        self.MainWindow.l_joint_scale.setText(str(config.joint_scale_default))
        self.MainWindow.l_text_size.setText(str(config.text_size_default))
        self.MainWindow.l_leader_distance.setText(str(config.leader_distance_default))
        
        self.MainWindow.l_inp_path.setText('')
        self.MainWindow.l_rpt_path.setText('')
        self.MainWindow.l_projName.setText('')
        self.MainWindow.list_hrs.clear()
        config.inpFile=None
        config.rptFile=None
        config.projName=None

    def proceed(self):
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

                msp.add_text(Head, height=config.text_size, dxfattribs={'color': color_head, "style": "epa2HydChart"}).set_placement((leader_up_end_x+6*config.text_size,leader_up_end_y+2*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
                msp.add_text(Pressure, height=config.text_size, dxfattribs={'color': color_pressure, "style": "epa2HydChart"}).set_placement((leader_up_end_x+6*config.text_size,leader_up_end_y-0.75*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
                self.MainWindow.browser_log.append(f'節點 {id} 壓力引線已完成繪圖')
        except:
            # print(i)
            pass
    
    def createBlocks(self, cad):
        tankBlock=cad.blocks.new(name='tank')
        tankBlock.add_polyline2d([(100,0), (100,100), (-100,100), (-100,0), (-50,0), (-50,-100), (50,-100), (50,0)], close=True)
        tankBlock.add_hatch().paths.add_polyline_path([(100,0), (100,100), (-100,100), (-100,0), (-50,0), (-50,-100), (50,-100), (50,0)], is_closed=True)

        reservoirBlock=cad.blocks.new(name='reservoir')
        reservoirBlock.add_polyline2d([(100,-50), (100,100), (85,100), (85,50), (-85,50), (-85,100), (-100,100), (-100,-50)], close=True)
        reservoirBlock.add_hatch().paths.add_polyline_path([(100,-50), (100,100), (85,100), (85,50), (-85,50), (-85,100), (-100,100), (-100,-50)], is_closed=True)

        junctionBlock=cad.blocks.new(name='junction')
        junctionBlock.add_ellipse((0,0), major_axis=(0,50), ratio=1)
        junctionBlock.add_hatch().paths.add_edge_path().add_ellipse((0,0), major_axis=(0,50), ratio=1)

        valveBlock=cad.blocks.new(name='valve')
        valveBlock.add_polyline2d([(0,0), (50,30), (50,-30)], close=True)
        valveBlock.add_polyline2d([(0,0), (-50,30), (-50,-30)], close=True)
        valveBlock.add_hatch().paths.add_polyline_path([(0,0), (50,30), (50,-30)], is_closed=True)
        valveBlock.add_hatch().paths.add_polyline_path([(0,0), (-50,30), (-50,-30)], is_closed=True)

        from ezdxf.enums import TextEntityAlignment
        from ezdxf.math import Vec2
        pumpBlock=cad.blocks.new(name='pump')
        pumpBlock.add_circle(Vec2(0,0), 100.0)
        pumpBlock.add_text("P", height=100, dxfattribs={"style": "epa2HydChart"}).set_placement((0,0), align=TextEntityAlignment.MIDDLE_CENTER)

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
            msp.add_text(elev, height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_up_end_x+6*config.text_size,leader_up_end_y+0.75*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            self.MainWindow.browser_log.append(f'節點 {id} 高程引線已完成繪圖')

    def demandLeader(self, color):
        from ezdxf.enums import TextEntityAlignment

        for i in range(0, len(df_Junctions)):
            QCoreApplication.processEvents()
            id=df_Junctions.at[i,'ID']
            x=float(df_Junctions.at[i,'x'])
            y=float(df_Junctions.at[i,'y'])

            l=df_NodeResults.index[df_NodeResults['ID']==id].tolist()[0]
            demand=df_NodeResults.at[l,'Demand']

            if demand != '0':
                leader_down_start_x=x+config.text_size
                leader_down_start_y=y-config.text_size

                leader_down_end_x=leader_down_start_x+config.leader_distance
                leader_down_end_y=leader_down_start_y-config.leader_distance
                
                msp.add_blockref('arrow', [leader_down_end_x,leader_down_end_y], dxfattribs={'xscale':config.block_scale, 'yscale':config.block_scale, 'rotation':225})
                msp.add_polyline2d([(leader_down_start_x,leader_down_start_y),(leader_down_end_x,leader_down_end_y)], dxfattribs={'color': color})
                msp.add_text(demand, height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_down_end_x+0.5*config.text_size, leader_down_end_y-0.5*config.text_size), align=TextEntityAlignment.TOP_LEFT)
                self.MainWindow.browser_log.append(f'節點 {id} 水量引線已完成繪圖')

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
            msp.add_text(head, height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_up_end_x+6*config.text_size,leader_up_end_y+2*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msp.add_text('ELEV', height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_up_end_x+6*config.text_size,leader_up_end_y+0.75*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msp.add_text('Pressure', height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_up_end_x+6*config.text_size,leader_up_end_y-0.75*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            self.MainWindow.browser_log.append(f'接水點 {id} 引線已完成繪圖')

    def pumpAnnotation(self, color):
        from ezdxf.enums import TextEntityAlignment
        for i in range(0, len(df_Pumps)):
            QCoreApplication.processEvents()
            id=df_Pumps.at[i,'ID']
            x=float(df_Pumps.at[i,'x'])
            y=float(df_Pumps.at[i,'y'])

            Q=float(df_Pumps.at[i,'Q'])
            H=float(df_Pumps.at[i,'H'])

            offset=[config.block_scale*100+0.75*config.text_size,
                    config.block_scale*100+2*config.text_size]

            msp.add_text(f'Q:{Q}', height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((x+2*config.text_size,y-offset[0]), align=TextEntityAlignment.MIDDLE_RIGHT)
            msp.add_text(f'H:{H}', height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((x+2*config.text_size,y-offset[1]), align=TextEntityAlignment.MIDDLE_RIGHT)
            self.MainWindow.browser_log.append(f'抽水機 {id} 已完成繪圖')

    def valveAnnotation(self, color):
        from ezdxf.enums import TextEntityAlignment
        for i in range(0, len(df_Valves)):
            QCoreApplication.processEvents()
            id=df_Valves.at[i,'ID']

            x1=float(df_Valves.at[i,'Node1_x'])
            y1=float(df_Valves.at[i,'Node1_y'])

            x2=float(df_Valves.at[i,'Node2_x'])
            y2=float(df_Valves.at[i,'Node2_y'])

            x=0.5*(x1+x2)
            y=0.5*(y1+y2)

            Type=df_Valves.at[i,'Type']
            Setting=df_Valves.at[i,'Setting']

            offset=[config.block_scale*50+0.75*config.text_size,
                    config.block_scale*50+2*config.text_size]

            msp.add_text(f'{Type}', height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((x,y-offset[0]), align=TextEntityAlignment.MIDDLE_CENTER)
            msp.add_text(f'{Setting}', height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((x,y-offset[1]), align=TextEntityAlignment.MIDDLE_CENTER)
            self.MainWindow.browser_log.append(f'閥件 {id} 已完成繪圖')

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
            msp.add_text(f'___T', height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_up_end_x+10*config.text_size,leader_up_end_y+3.25*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msp.add_text(f'Hwl:{maxElev}', height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_up_end_x+10*config.text_size,leader_up_end_y+2*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msp.add_text(f'Mwl:{minElev}', height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_up_end_x+10*config.text_size,leader_up_end_y+0.75*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            msp.add_text(f'Elev:{elev}', height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_up_end_x+10*config.text_size,leader_up_end_y-0.75*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
            self.MainWindow.browser_log.append(f'水池 {id} 已完成繪圖')

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
        from ezdxf.enums import TextEntityAlignment
        text_x=(start_x+end_x)/2
        text_y=(start_y+end_y)/2
        diameter=df_Pipes.at[i, 'Diameter']
        length=df_Pipes.at[i, 'Length']
        text_up=f'{diameter}-{length}'
        rotation_text = self.rotation_text(start_x, start_y, end_x, end_y)
        msp.add_text(text_up, height=config.text_size, rotation=rotation_text, dxfattribs={"style": "epa2HydChart"}).set_placement((text_x, text_y), align=TextEntityAlignment.BOTTOM_CENTER)

    def flowString(self, id, start_x, start_y, end_x, end_y):
        from ezdxf.enums import TextEntityAlignment
        try:
            text_x=(start_x+end_x)/2
            text_y=(start_y+end_y)/2

            link_row=df_LinkResults.index[df_LinkResults['ID']==id].tolist()[0]

            flow=float(df_LinkResults.at[link_row, 'Flow'])
            rotation_text = self.rotation_text(start_x, start_y, end_x, end_y)

            import math
            rotation=math.atan2(end_y-start_y, end_x-start_x)
            rotation=math.degrees(rotation)
            if rotation<0:
                rotation+=360

            if 90<rotation<270:
                direction = '<---' if flow >=0 else '--->'
            else:
                direction = '--->' if flow >=0 else '<---'

            flow = flow if flow>=0 else -1*flow

            headloss=float(df_LinkResults.at[link_row, 'Headloss'])
            # unitHeadloss=float(df_LinkResults.at[link_row, 'unitHeadloss'])

            # pipe_row=df_Pipes.index[df_Pipes['ID']==id].tolist()[0]
            # length=float(df_Pipes.at[pipe_row, 'Length'])
            # headloss=length*unitHeadloss/1000
            # headloss=f'{headloss:.2f}'
            text_up=f'{flow} ({headloss:.2f}) {direction}'

            msp.add_text(text_up, height=config.text_size, rotation=rotation_text, dxfattribs={"style": "epa2HydChart"}).set_placement((text_x, text_y), align=TextEntityAlignment.TOP_CENTER)
        except:
            self.MainWindow.browser_log.append(f'[Error]管線 {id} 錯誤，請重新匯出inp及rpt檔後重試')

    def rotation_text(self, start_x, start_y, end_x, end_y):
        import math
        rotation=math.atan2(end_y-start_y, end_x-start_x)
        rotation=math.degrees(rotation)
        if rotation<0:
            rotation+=360
        if 90<rotation<270:
            rotation_text=rotation-180
        else:
            rotation_text=rotation
        return rotation_text

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
                self.MainWindow.browser_log.append(f'管線 {link_id} 已完成繪圖')
            
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
                    self.MainWindow.browser_log.append(f'水池 {id} 圖塊已插入')

            if item == 'reservoir':
                df=df_Reservoirs
                for i in range (0, len(df)):
                    QCoreApplication.processEvents()
                    id=df.at[i,'ID']
                    x=float(df.at[i,'x'])
                    y=float(df.at[i,'y'])
                    msp.add_blockref(item, [x,y], dxfattribs={'xscale':config.block_scale, 'yscale':config.block_scale})
                    self.MainWindow.browser_log.append(f'接水點 {id} 圖塊已插入')

            if item == 'pump':
                df=df_Pumps
                for i in range (0, len(df)):
                    QCoreApplication.processEvents()
                    id=df.at[i,'ID']
                    x=float(df.at[i,'x'])
                    y=float(df.at[i,'y'])
                    msp.add_blockref(item, [x,y], dxfattribs={'xscale':config.block_scale, 'yscale':config.block_scale})
                    self.MainWindow.browser_log.append(f'抽水機 {id} 圖塊已插入')

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
                    self.MainWindow.browser_log.append(f'閥件 {id} 圖塊已插入')

            if item == 'junction':
                df=df_Junctions
                for i in range (0, len(df)):
                    QCoreApplication.processEvents()
                    id=df.at[i,'ID']
                    x=float(df.at[i,'x'])
                    y=float(df.at[i,'y'])
                    msp.add_blockref(item, [x,y], dxfattribs={'xscale':config.joint_scale, 'yscale':config.joint_scale})
                    self.MainWindow.browser_log.append(f'節點 {id} 圖塊已插入')
                
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
        # text=text.replace('-', ' -')
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
            df_Coords['x'] = df_Coords['x'].astype(float)
            df_Coords['y'] = df_Coords['y'].astype(float)
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
                'x':[float(d[1])],
                'y':[float(d[2])],
                }
            new_df=pd.DataFrame.from_dict(data)
            df=pd.concat([df,new_df])
        df=df.reset_index(drop=True)
        return df

    def readPipes(self, inpFile):
        try:
            start, end=self.lineStartEnd(inpFile, '[PIPES]', '[PUMPS]',2,2)
            lines = open(inpFile).readlines()
            df=pd.DataFrame(columns=['ID','Node1','Node2', 'Length', 'Diameter', 'Node1_x', 'Node1_y', 'Node2_x', 'Node2_y', 'Roughness'])
            for l in range (start-1, end):
                d=self.line2dict(lines, l)
                data={
                    'ID':[d[1]],
                    'Node1':[d[2]],
                    'Node2':[d[3]],
                    'Length':[d[4]],
                    'Diameter':[d[5]],
                    'Roughness':[d[6]]
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
        except:
            # print([d[1]])
            pass
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
        df=pd.DataFrame(columns=['ID', 'Elev', 'BaseDemand', 'x', 'y'])
        for l in range (start-1, end):
            d=self.line2dict(lines, l)
            data={
                'ID':d[1],
                'Elev':d[2],
                'BaseDemand':d[3]
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
        df=pd.DataFrame(columns=['ID', 'Node1', 'Node2', 'Node1_x', 'Node1_y', 'Node2_x', 'Node2_y', 'Type', 'Setting'])
        for l in range (start-1, end):
            d=self.line2dict(lines, l)

            id=d[1]
            Node1=d[2]
            Node2=d[3]
            Type=d[5]
            Setting=d[6]
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
                'Type':Type,
                'Setting':Setting
                }
            if df.empty:
                df.loc[0]=data
            else:
                df.loc[len(df)]=data
        df=df.reset_index(drop=True)
        return df

    def readPumps(self, inpFile):
        lines = open(inpFile).readlines()

        start_curve, end_curve=self.lineStartEnd(inpFile, '[CURVES]', '[CONTROLS]',2,1)
        df_pumpCurves=pd.DataFrame(columns=['ID', 'Q', 'H'])
        for l in range (start_curve-1, end_curve):
            if 'PUMP' in lines[l]:
                continue
            elif '\n' == lines[l]:
                continue
            else:
                d=self.line2dict(lines, l)
                ID=d[1]
                Q=d[2]
                H=d[3]
            data_curve={
                'ID':ID,
                'Q':Q,
                'H':H
                }
            if df_pumpCurves.empty:
                df_pumpCurves.loc[0]=data_curve
            else:
                df_pumpCurves.loc[len(df_pumpCurves)]=data_curve
        df_pumpCurves=df_pumpCurves.reset_index(drop=True)

        start, end=self.lineStartEnd(inpFile, '[PUMPS]', '[VALVES]',2,2)
        df=pd.DataFrame(columns=['ID', 'Node1', 'Node2', 'Node1_x', 'Node1_y', 'Node2_x', 'Node2_y', 'x', 'y', 'Q', 'H'])
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

            curveID=d[5]
            i=int(df_pumpCurves.index[df_pumpCurves['ID']==curveID][0])
            Q=df_pumpCurves.at[i,'Q']
            H=df_pumpCurves.at[i,'H']
            
            data={
                'ID':ID,
                'Node1':Node1,
                'Node2':Node2,
                'Node1_x':Node1_x,
                'Node1_y':Node1_y,
                'Node2_x':Node2_x,
                'Node2_y':Node2_y,
                'x':x,
                'y':y,
                'Q':Q,
                'H':H
                }
            if df.empty:
                df.loc[0]=data
            else:
                df.loc[len(df)]=data
        df=df.reset_index(drop=True)
        return df

    def readNodeResults(self, *args, **kwargs):
        hr = kwargs.get('hr')
        rptFile = kwargs.get('input')

        if hr==None:
            start_str='Node Results:'
            end_str='Link Results:'
        else:
            start_str=f'Node Results at {hr} Hrs:'
            end_str=f'Link Results at {hr} Hrs:'
        start, end=self.lineStartEnd(rptFile, start_str, end_str,5,2)
        lines = open(rptFile).readlines()
        df=pd.DataFrame(columns=['ID', 'Demand', 'Head', 'Pressure'])
        for l in range (start-1, end):
            d=self.line2dict(lines, l)
            try:
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

            except:
                self.MainWindow.browser_log.append(f'[Error]節點 {id} 錯誤，請手動修正.rpt檔內容')
                QMessageBox.warning(None, '警告', f'節點{id}資料錯誤，請手動修正.rpt檔內容')

                data={
                    'ID':id,
                    'Demand':None,
                    'Head':None,
                    'Pressure':None,
                    }
                # print(f'error id:{id}')
                
            if df.empty:
                df.loc[0]=data
            else:
                df.loc[len(df)]=data
        df=df.reset_index(drop=True)
        return df

    def readLinkResults(self, *args, **kwargs):
        hr1=kwargs.get('hr1')
        hr2=kwargs.get('hr2')
        rptFile=kwargs.get('input')
        
        if hr1==None:     # without patteren
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
        df=pd.DataFrame(columns=['ID', 'Flow', 'unitHeadloss', 'Headloss'])
        for l in range (start-1, end):
            d=self.line2dict(lines, l)
            pipe_id=d[1]
            flow=d[2]
            unitHeadloss=d[4]

            # calculate headloss number:
            if pipe_id in df_Pipes['ID'].tolist():   # 2 side in link are node:
                pipe_index=df_Pipes.index[df_Pipes['ID']==pipe_id].tolist()[0]
                node1=df_Pipes.at[pipe_index, 'Node1']
                i1=df_NodeResults.index[df_NodeResults['ID']==node1].tolist()[0]
                node2=df_Pipes.at[pipe_index, 'Node2']
                i2=df_NodeResults.index[df_NodeResults['ID']==node2].tolist()[0]

                from decimal import Decimal
                try:
                    node1_head=Decimal(df_NodeResults.at[i1, 'Head'])
                    node2_head=Decimal(df_NodeResults.at[i2, 'Head'])

                    Headloss=float(abs(node2_head-node1_head))
                except:
                    Headloss=0

            data={
                'ID':pipe_id,
                'Flow':flow,
                'unitHeadloss':unitHeadloss,
                'Headloss':Headloss
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

    def save_svg(self, *args, **kwargs):
        msp=kwargs.get('msp')
        cad=kwargs.get('cad')
        svgPath=kwargs.get('path')
        from ezdxf.addons.drawing import Frontend, RenderContext, svg, layout, config
        msp = cad.modelspace()
        context = RenderContext(cad)
        backend = svg.SVGBackend()
        cfg = config.Configuration(
            background_policy=config.BackgroundPolicy.WHITE,
        )
        frontend = Frontend(context, backend, config=cfg)
        frontend.draw_layout(msp)
        page = layout.Page(0, 0, layout.Units.mm, margins=layout.Margins.all(10))
        svg_string = backend.get_string(
            page, settings=layout.Settings(scale=1, fit_page=False)
        )

        with open(svgPath, "wt", encoding="utf8") as fp:
            fp.write(svg_string)

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)   # Enable high DPI
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())