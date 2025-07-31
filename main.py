
import ezdxf
import sys, warnings, traceback

from ui import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QLabel
from PyQt6.QtGui import QIntValidator, QDoubleValidator
from PyQt6.QtCore import QCoreApplication, Qt

import config, utils
from process_utils import process1
from load_button import loadinpButton, loadrptButton
import read_utils
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.MainWindow = Ui_MainWindow()
        self.MainWindow.setupUi(self)
        self.MainWindow.b_browser_inp.clicked.connect(lambda:loadinpButton(self))
        self.MainWindow.b_browser_rpt.clicked.connect(lambda:loadrptButton(self))
        self.MainWindow.b_reset.clicked.connect(self.resetButton)
        self.MainWindow.b_draw.clicked.connect(self.processButton)
        self.MainWindow.l_block_size.setText(str(config.block_scale_default))
        self.MainWindow.l_block_size.setValidator(QDoubleValidator())
        self.MainWindow.l_joint_size.setText(str(config.joint_scale_default))
        self.MainWindow.l_joint_size.setValidator(QDoubleValidator())
        self.MainWindow.l_text_size.setText(str(config.text_size_default))
        self.MainWindow.l_text_size.setValidator(QDoubleValidator())
        self.MainWindow.l_leader_distance.setText(str(config.leader_distance_default))
        self.MainWindow.l_leader_distance.setValidator(QIntValidator())
        self.MainWindow.chk_autoSize.stateChanged.connect(lambda:utils.autoSize(self))
        self.MainWindow.comboBox_digits.setCurrentText('0.00')
        # self.MainWindow.l_inp_path.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        # self.MainWindow.l_inp_path.setToolTip(self.MainWindow.l_inp_path.text())
        # self.MainWindow.l_rpt_path.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        # self.MainWindow.l_rpt_path.setToolTip(self.MainWindow.l_rpt_path.text())


    def setLogToButton(self):
        self.MainWindow.browser_log.verticalScrollBar().setValue(self.MainWindow.browser_log.verticalScrollBar().maximum())

    def createModelspace(self, *args, **kwargs):
        global msp

        try:
            cad = ezdxf.new()
            msp = cad.modelspace()
            cad.styles.new("epa2HydChart", dxfattribs={"font" : "Microsoft JhengHei"})

            return cad, msp
        except Exception as e:
            traceback.print_exc()

    def addTitle(self, *args, **kwargs):
        try:
            hr=kwargs.get('hr_str')

            # 計算左上角座標
            xs=config.df_Coords['x'].tolist()+config.df_Vertices['x'].tolist()
            x_min=min(xs)

            ys=config.df_Coords['y'].tolist()+config.df_Vertices['y'].tolist()
            y_max=max(ys)

            projName=self.MainWindow.l_projName.text()

            # 計算Q值
            from decimal import Decimal
            Q=0
            for i in range(0, len(config.df_Junctions)):
                id=config.df_Junctions.at[i,'ID']
                row=config.df_NodeResults.index[config.df_NodeResults['ID']==id].tolist()[0]
                if config.df_NodeResults.at[row, 'Demand'] != None:
                    Q=Q+Decimal(config.df_NodeResults.at[row, 'Demand'])
                else:
                    msg= f'[Error]節點 {id} Demand數值錯誤，Q值總計可能有誤'
                    utils.renew_log(self, msg, True)

            # 匯整C值
            C_str=''
            Cs=config.df_Pipes['Roughness'].unique()
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
        except Exception as e:
            traceback.print_exc()


    def convertSVGtoPNG(self, *args, **kwargs):
        try:
            # msp=kwargs.get('msp')
            # cad=kwargs.get('cad')
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
        except Exception as e:
            traceback.print_exc()

    
    def resetButton(self):
        self.MainWindow.l_block_size.setText(str(config.block_scale_default))
        self.MainWindow.l_joint_size.setText(str(config.joint_scale_default))
        self.MainWindow.l_text_size.setText(str(config.text_size_default))
        self.MainWindow.l_leader_distance.setText(str(config.leader_distance_default))
        self.MainWindow.chk_export_0cmd.setChecked(True)
        self.MainWindow.chk_autoSize.setChecked(False)
        
        self.MainWindow.l_inp_path.setText('')
        self.MainWindow.l_rpt_path.setText('')
        self.MainWindow.l_projName.setText('')
        self.MainWindow.list_hrs.clear()
        config.inpFile=None
        config.rptFile=None
        config.projName=None

    def processButton(self):
        config.block_scale=float(self.MainWindow.l_block_size.text())
        config.joint_scale=float(self.MainWindow.l_joint_size.text())
        config.text_size=float(self.MainWindow.l_text_size.text())
        config.leader_distance=float(self.MainWindow.l_leader_distance.text())
        
        process1(self)

    def headPressureLeader(self, *args, **kwargs):
        from ezdxf.enums import TextEntityAlignment
        color=kwargs.get('color')

        try:
            for i in range(0, len(config.df_Junctions)):
                id=config.df_Junctions.at[i,'ID']
                start_x=float(config.df_Junctions.at[i,'x'])
                start_y=float(config.df_Junctions.at[i,'y'])
                result_row=config.df_NodeResults.index[config.df_NodeResults['ID']==str(id)].tolist()[0]
                Head=config.df_NodeResults.at[result_row,'Head']
                Pressure=config.df_NodeResults.at[result_row,'Pressure']

                if float(Pressure)<0:
                    color_pressure=1
                else:
                    color_pressure=color

                if float(Head)<0:
                    color_head=1
                else:
                    color_head=color

                leader_up_start_x=start_x+config.text_size
                leader_up_start_y=start_y+config.text_size

                leader_up_end_x=leader_up_start_x+config.leader_distance
                leader_up_end_y=leader_up_start_y+config.leader_distance

                msp.add_text(Head, height=config.text_size, dxfattribs={'color': color_head, "style": "epa2HydChart"}).set_placement((leader_up_end_x+6*config.text_size,leader_up_end_y+2*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
                msp.add_text(Pressure, height=config.text_size, dxfattribs={'color': color_pressure, "style": "epa2HydChart"}).set_placement((leader_up_end_x+6*config.text_size,leader_up_end_y-0.75*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
                msg= f'節點 {id} 高度及壓力引線已完成繪圖'
                utils.renew_log(self, msg, False)
        except Exception as e:
            traceback.print_exc()
    
    def createBlocks(self, cad):
        try:
            tankBlock=cad.blocks.new(name='tank')
            tankBlock.add_polyline2d([(0.5,0), (0.5,0.5), (-0.5,0.5), (-0.5,0), (-0.25,0), (-0.25,-0.5), (0.25,-0.5), (0.25,0)], close=True)
            tankBlock.add_hatch().paths.add_polyline_path([(0.5,0), (0.5,0.5), (-0.5,0.5), (-0.5,0), (-0.25,0), (-0.25,-0.5), (0.25,-0.5), (0.25,0)], is_closed=True)

            reservoirBlock=cad.blocks.new(name='reservoir')
            reservoirBlock.add_polyline2d([(0.5,-0.25), (0.5,0.5), (0.4,0.5), (0.4,0.25), (-0.4,0.25), (-0.4,0.5), (-0.5,0.5), (-0.5,-0.25)], close=True)
            reservoirBlock.add_hatch().paths.add_polyline_path([(0.5,-0.25), (0.5,0.5), (0.4,0.5), (0.4,0.25), (-0.4,0.25), (-0.4,0.5), (-0.5,0.5), (-0.5,-0.25)], is_closed=True)

            junctionBlock=cad.blocks.new(name='junction')
            junctionBlock.add_ellipse((0,0), major_axis=(0,0.5), ratio=1)
            junctionBlock.add_hatch().paths.add_edge_path().add_ellipse((0,0), major_axis=(0,0.5), ratio=1)

            valveBlock=cad.blocks.new(name='valve')
            valveBlock.add_polyline2d([(0,0), (0.5,0.3), (0.5,-0.3)], close=True)
            valveBlock.add_polyline2d([(0,0), (-0.5,0.3), (-0.5,-0.3)], close=True)
            valveBlock.add_hatch().paths.add_polyline_path([(0,0), (0.5,0.3), (0.5,-0.3)], is_closed=True)
            valveBlock.add_hatch().paths.add_polyline_path([(0,0), (-0.5,0.3), (-0.5,-0.3)], is_closed=True)

            flowDirectionArrowBlock=cad.blocks.new(name='flowDirectionArrow')
            # flowDirectionArrowBlock.add_polyline2d([(-1,0.5), (0,0), (-1,-0.5)], close=False)
            flowDirectionArrowBlock.add_polyline2d([(0,0), (-1,0.5), (-1,-0.5)], close=True)
            flowDirectionArrowBlock.add_hatch().paths.add_polyline_path([(0,0), (-1,0.5), (-1,-0.5)], is_closed=True)

            from ezdxf.enums import TextEntityAlignment
            from ezdxf.math import Vec2
            pumpBlock=cad.blocks.new(name='pump')
            pumpBlock.add_circle(Vec2(0,0), 0.5)
            pumpBlock.add_text("P", height=0.8, dxfattribs={"style": "epa2HydChart"}).set_placement((0,0), align=TextEntityAlignment.MIDDLE_CENTER)
        except Exception as e:
            traceback.print_exc()

    def elevAnnotation(self, *args, **kwargs):
        from ezdxf.enums import TextEntityAlignment
        color= kwargs.get('color')

        try:
            for i in range(0, len(config.df_Junctions)):
                id=config.df_Junctions.at[i,'ID']
                x=float(config.df_Junctions.at[i,'x'])
                y=float(config.df_Junctions.at[i,'y'])
                elev=config.df_Junctions.at[i,'Elev']

                leader_up_start_x=x+config.text_size
                leader_up_start_y=y+config.text_size

                leader_up_end_x=leader_up_start_x+config.leader_distance
                leader_up_end_y=leader_up_start_y+config.leader_distance

                msp.add_polyline2d([(leader_up_start_x,leader_up_start_y),
                                    (leader_up_end_x,leader_up_end_y),
                                    (leader_up_end_x+6*config.text_size,leader_up_end_y)], dxfattribs={'color': color})
                msp.add_text(elev, height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_up_end_x+6*config.text_size,leader_up_end_y+0.75*config.text_size), align=TextEntityAlignment.MIDDLE_RIGHT)
                msg= f'節點 {id} 高程引線已完成繪圖'
                utils.renew_log(self, msg, False)
        except Exception as e:
            traceback.print_exc()

    def demandLeader(self, *args, **kwargs):
        
        try:
            color=kwargs.get('color')
            draw0cmd=kwargs.get('draw0cmd')

            for i in range(0, len(config.df_Junctions)):
                id=config.df_Junctions.at[i,'ID']
                x=float(config.df_Junctions.at[i,'x'])
                y=float(config.df_Junctions.at[i,'y'])

                l=config.df_NodeResults.index[config.df_NodeResults['ID']==id].tolist()[0]
                demand=config.df_NodeResults.at[l,'Demand']

                if draw0cmd:
                    self.drawDemandLeader(color, id, x, y, demand, True)
                    self.setLogToButton()
                else:
                    self.drawDemandLeader(color, id, x, y, demand, False)
                    self.setLogToButton()
                
                QCoreApplication.processEvents()
        except Exception as e:
            traceback.print_exc()

    def drawDemandLeader(self, color, id, x, y, demand, export0cmd:bool):
        from ezdxf.enums import TextEntityAlignment

        try:
            if (export0cmd) or (export0cmd==False and float(demand)!=0.0):
                leader_down_start_x=x+config.text_size
                leader_down_start_y=y-config.text_size

                leader_down_end_x=leader_down_start_x+config.leader_distance
                leader_down_end_y=leader_down_start_y-config.leader_distance
                        
                msp.add_blockref('demandArrow', [leader_down_end_x,leader_down_end_y], dxfattribs={'xscale':config.block_scale, 'yscale':config.block_scale, 'rotation':225})
                msp.add_polyline2d([(leader_down_start_x,leader_down_start_y),(leader_down_end_x,leader_down_end_y)], dxfattribs={'color': color})
                msp.add_text(demand, height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((leader_down_end_x+0.5*config.text_size, leader_down_end_y-0.5*config.text_size), align=TextEntityAlignment.TOP_LEFT)
                self.MainWindow.browser_log.append(f'節點 {id} 水量引線已完成繪圖')
            elif export0cmd==False and float(demand)==0.0:
                pass
        except Exception as e:
            traceback.print_exc()

    def reservoirsLeader(self, *args, **kwargs):
        from ezdxf.enums import TextEntityAlignment

        color= kwargs.get('color')
        digits= kwargs.get('digits')

        try:
            for i in range(0, len(config.df_Reservoirs)):
                id=config.df_Reservoirs.at[i,'ID']
                x=float(config.df_Reservoirs.at[i,'x'])
                y=float(config.df_Reservoirs.at[i,'y'])
                head=float(config.df_Reservoirs.at[i,'Head'])
                head=f'{head:.{digits}f}'

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
                msg=f'接水點 {id} 引線已完成繪圖'
                utils.renew_log(self, msg, False)
        except Exception as e:
            traceback.print_exc()

    def pumpAnnotation(self, *args, **kwargs):
        from ezdxf.enums import TextEntityAlignment
        color=kwargs.get('color')
        digits=kwargs.get('digits')
        try:
            for i in range(0, len(config.df_Pumps)):
                id=config.df_Pumps.at[i,'ID']
                x=float(config.df_Pumps.at[i,'x'])
                y=float(config.df_Pumps.at[i,'y'])

                Q=float(config.df_Pumps.at[i,'Q'])
                H=float(config.df_Pumps.at[i,'H'])

                Q_str=f"{Q:.{digits}f}"
                H_str=f"{H:.{digits}f}"

                offset=[config.block_scale+0.75*config.text_size,
                        config.block_scale+2*config.text_size]

                msp.add_text(f'Q:{Q_str}', height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((x+2*config.text_size,y-offset[0]), align=TextEntityAlignment.MIDDLE_RIGHT)
                msp.add_text(f'H:{H_str}', height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((x+2*config.text_size,y-offset[1]), align=TextEntityAlignment.MIDDLE_RIGHT)
                msg= f'抽水機 {id} 已完成繪圖'
                utils.renew_log(self, msg, False)
        except Exception as e:
            traceback.print_exc()

    def valveAnnotation(self, color):
        from ezdxf.enums import TextEntityAlignment
        try:
            for i in range(0, len(config.df_Valves)):
                id=config.df_Valves.at[i,'ID']

                x1=float(config.df_Valves.at[i,'Node1_x'])
                y1=float(config.df_Valves.at[i,'Node1_y'])

                x2=float(config.df_Valves.at[i,'Node2_x'])
                y2=float(config.df_Valves.at[i,'Node2_y'])

                x=0.5*(x1+x2)
                y=0.5*(y1+y2)

                Type=config.df_Valves.at[i,'Type']
                Setting=config.df_Valves.at[i,'Setting']

                offset=[config.block_scale+0.75*config.text_size,
                        config.block_scale+2*config.text_size]

                msp.add_text(f'{Type}', height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((x,y-offset[0]), align=TextEntityAlignment.MIDDLE_CENTER)
                msp.add_text(f'{Setting}', height=config.text_size, dxfattribs={'color': color, "style": "epa2HydChart"}).set_placement((x,y-offset[1]), align=TextEntityAlignment.MIDDLE_CENTER)
                msg= f'閥件 {id} 已完成繪圖'
                utils.renew_log(self, msg, False)
        except Exception as e:
            traceback.print_exc()

    def tankLeader(self, *args, **kwargs):
        from ezdxf.enums import TextEntityAlignment

        color= kwargs.get('color')
        digits= kwargs.get('digits')
        try:
            for i in range(0, len(config.df_Tanks)):
                id=config.df_Tanks.at[i,'ID']
                x=float(config.df_Tanks.at[i,'x'])
                y=float(config.df_Tanks.at[i,'y'])

                elev=float(config.df_Tanks.at[i,'Elev'])
                elev=f'{elev:.{digits}f}'

                minElev=float(config.df_Tanks.at[i,'MinElev'])
                minElev=f'{minElev:.{digits}f}'

                maxElev=float(config.df_Tanks.at[i,'MaxElev'])
                maxElev=f'{maxElev:.{digits}f}'

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
                msg= f'水池 {id} 引線已完成繪圖'
                utils.renew_log(self, msg, False)
        except Exception as e:
            traceback.print_exc()

    def pipeAnnotationBlock(self, link_id, start_x, start_y, end_x, end_y, i):

        try:
            center_x=(start_x+end_x)/2
            center_y=(start_y+end_y)/2
            diameter=config.df_Pipes.at[i, 'Diameter']
            length=config.df_Pipes.at[i, 'Length']

            link_row=config.df_LinkResults.index[config.df_LinkResults['ID']==link_id].tolist()[0]
            flow=float(config.df_LinkResults.at[link_row, 'Flow'])

            import math
            rotation=math.atan2(end_y-start_y, end_x-start_x)
            rotation=math.degrees(rotation)

            if rotation<0:
                rotation+=360

            if rotation > 90 and rotation < 270:
                rotation_annotaion=rotation-180
            else:
                rotation_annotaion=rotation

            headloss=config.df_LinkResults.at[link_row, 'Headloss']

            attrib={"char_height": config.text_size,
                    "style": "epa2HydChart",
                    "attachment_point":5,
                    "line_spacing_factor":1.5,
                    'rotation':rotation_annotaion}
    
            text=f"""{diameter}-{length}\n{abs(flow)} ({headloss})"""

            msp.add_mtext(text, dxfattribs=attrib).set_location(insert=(center_x, center_y))

            if flow>=0:
                msp.add_blockref('flowDirectionArrow', [center_x,center_y], dxfattribs={'xscale':config.text_size, 'yscale':config.text_size, 'rotation':rotation})
            else:
                msp.add_blockref('flowDirectionArrow', [center_x,center_y], dxfattribs={'xscale':config.text_size, 'yscale':config.text_size, 'rotation':rotation+180})

        except Exception as e:
            print(e)
            msg=f'[Error]管線 {id} 錯誤，請重新匯出inp及rpt檔後重試'
            utils.renew_log(self, msg, True)
            traceback.print_exc()

    def pipeAnnotation(self):
        try:
            # Convert LINK column to set for O(1) lookups
            link_ids = set(config.df_Vertices['LINK'])

            # Group by LINK for fast access
            vertices_dict = config.df_Vertices.groupby('LINK')[['x', 'y']].apply(lambda g: list(zip(g['x'], g['y']))).to_dict()

            for i, row in config.df_Pipes.iterrows():
                link_id = row['ID']

                if link_id in link_ids:
                    verts = vertices_dict[link_id]
                    num_verts = len(verts)

                    if num_verts == 1:  # 1 vertex
                        start_x, start_y = float(row['Node1_x']), float(row['Node1_y'])
                        end_x, end_y = verts[0]  # First and only vertex

                    elif num_verts % 2 == 0:  # Even number of vertices
                        mid = num_verts // 2
                        start_x, start_y = verts[mid - 1]
                        end_x, end_y = verts[mid]

                    else:  # Odd number of vertices
                        mid = num_verts // 2
                        start_x, start_y = verts[mid - 1]
                        end_x, end_y = verts[mid]

                else:  # No vertices
                    start_x, start_y = float(row['Node1_x']), float(row['Node1_y'])
                    end_x, end_y = float(row['Node2_x']), float(row['Node2_y'])

                # Call annotation function once per pipe
                self.pipeAnnotationBlock(link_id, start_x, start_y, end_x, end_y, i)
        except Exception as e:
            traceback.print_exc()

    def rotation_text(self, start_x, start_y, end_x, end_y):
        import math
        try:
            rotation=math.atan2(end_y-start_y, end_x-start_x)
            rotation=math.degrees(rotation)
            if rotation<0:
                rotation+=360
            if 90<rotation<270:
                rotation_text=rotation-180
            else:
                rotation_text=rotation
            return rotation_text
        except Exception as e:
            traceback.print_exc()

    def pipeLines(self):
        try:
            for i in range(0, len(config.df_Pipes)):
                start_x=float(config.df_Pipes.at[i, 'Node1_x'])
                start_y=float(config.df_Pipes.at[i, 'Node1_y'])
                end_x=float(config.df_Pipes.at[i, 'Node2_x'])
                end_y=float(config.df_Pipes.at[i, 'Node2_y'])

                link_id=config.df_Pipes.at[i, 'ID']
                if link_id in config.df_Vertices['LINK'].tolist():
                    rows=config.df_Vertices.index[config.df_Vertices['LINK']==link_id].tolist()
                    firstVert_x=float(config.df_Vertices.at[rows[0],'x'])
                    firstVert_y=float(config.df_Vertices.at[rows[0],'y'])
                    msp.add_polyline2d([(start_x,start_y), (firstVert_x,firstVert_y)])
                    for j in rows[:len(rows)-1]:
                        x1=float(config.df_Vertices.at[j,'x'])
                        y1=float(config.df_Vertices.at[j,'y'])
                        x2=float(config.df_Vertices.at[j+1,'x'])
                        y2=float(config.df_Vertices.at[j+1,'y'])
                        msp.add_polyline2d([(x1,y1), (x2,y2)])
                
                    lastVert_x=float(config.df_Vertices.at[rows[len(rows)-1],'x'])
                    lastVert_y=float(config.df_Vertices.at[rows[len(rows)-1],'y'])
                    msp.add_polyline2d([(lastVert_x,lastVert_y), (end_x,end_y)])
                    msg= f'管線 {link_id} 已完成繪圖'
                    utils.renew_log(self, msg, False)                
                else:
                    msp.add_polyline2d([(end_x,end_y), (start_x,start_y)])

                QCoreApplication.processEvents()
        except Exception as e:
            traceback.print_exc()

    def insertBlocks(self):
        try:
            for item in ['tank', 'reservoir', 'junction', 'pump', 'valve']:
                if item == 'tank':
                    df=config.df_Tanks
                    for i in range (0, len(df)):
                        id=df.at[i,'ID']
                        x=float(df.at[i,'x'])
                        y=float(df.at[i,'y'])
                        msp.add_blockref(item, [x,y], dxfattribs={'xscale':config.block_scale, 'yscale':config.block_scale})
                        msg= f'水池 {id} 圖塊已插入'
                        utils.renew_log(self, msg, False)

                if item == 'reservoir':
                    df=config.df_Reservoirs
                    for i in range (0, len(df)):
                        id=df.at[i,'ID']
                        x=float(df.at[i,'x'])
                        y=float(df.at[i,'y'])
                        msp.add_blockref(item, [x,y], dxfattribs={'xscale':config.block_scale, 'yscale':config.block_scale})
                        msg= f'接水點 {id} 圖塊已插入'
                        utils.renew_log(self, msg, False)

                if item == 'pump':
                    df=config.df_Pumps
                    for i in range (0, len(df)):
                        id=df.at[i,'ID']
                        x=float(df.at[i,'x'])
                        y=float(df.at[i,'y'])
                        msp.add_blockref(item, [x,y], dxfattribs={'xscale':config.block_scale, 'yscale':config.block_scale})
                        msg= f'抽水機 {id} 圖塊已插入'
                        utils.renew_log(self, msg, False)

                if item == 'valve':
                    import math
                    df=config.df_Valves
                    for i in range (0, len(df)):
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
                        msg= f'閥件 {id} 圖塊已插入'
                        utils.renew_log(self, msg, False)

                if item == 'junction':
                    df=config.df_Junctions
                    for i in range (0, len(df)):
                        id=df.at[i,'ID']
                        x=float(df.at[i,'x'])
                        y=float(df.at[i,'y'])
                        msp.add_blockref(item, [x,y], dxfattribs={'xscale':config.joint_scale, 'yscale':config.joint_scale})
                        msg= f'節點 {id} 圖塊已插入'
                        utils.renew_log(self, msg, False)
        except Exception as e:
            traceback.print_exc()
                


    def save_svg(self, *args, **kwargs):
        try:
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
        except Exception as e:
            traceback.print_exc()

warnings.simplefilter(action='ignore', category=FutureWarning)
# QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)   # Enable high DPI
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
