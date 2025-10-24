
import ezdxf
from ezdxf.document import Drawing
from ezdxf.layouts import Modelspace
import sys, warnings, traceback

# Suppress PyQt6 SIP deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")

from ui import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QLabel
from PyQt6.QtGui import QIntValidator, QDoubleValidator
from PyQt6.QtCore import QCoreApplication, Qt

import globals, utils
from process_utils import process1
from load_button import loadinpButton, loadrptButton
import read_utils
import log
import progress_utils

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.MainWindow = Ui_MainWindow()
        self.MainWindow.setupUi(self)
        
        # Set the main window instance in config
        globals.main_window = self
        
        self.MainWindow.b_browser_inp.clicked.connect(lambda:loadinpButton())
        self.MainWindow.b_browser_rpt.clicked.connect(lambda:loadrptButton())
        self.MainWindow.b_reset.clicked.connect(self.resetButton)
        self.MainWindow.b_draw.clicked.connect(self.processButton)
        self.MainWindow.l_block_size.setText(str(globals.BLOCK_SIZE_DEFAULT))
        self.MainWindow.l_block_size.setValidator(QDoubleValidator())
        self.MainWindow.l_joint_size.setText(str(globals.JOINT_SIZE_DEFAULT))
        self.MainWindow.l_joint_size.setValidator(QDoubleValidator())
        self.MainWindow.l_text_size.setText(str(globals.TEXT_SIZE_DEFAULT))
        self.MainWindow.l_text_size.setValidator(QDoubleValidator())
        self.MainWindow.l_leader_distance.setText(str(globals.LEADER_DISTANCE_DEFAULT))
        self.MainWindow.l_leader_distance.setValidator(QIntValidator())
        self.MainWindow.l_line_width.setText(str(globals.LINE_WIDTH_DEFAULT))
        self.MainWindow.l_line_width.setValidator(QIntValidator())
        self.MainWindow.chk_autoSize.stateChanged.connect(lambda:utils.autoSize())
        self.MainWindow.comboBox_digits.setCurrentText('0.00')
        
    def createModelspace(self, *args, **kwargs):
        try:
            cad: Drawing = ezdxf.new()
            msp: Modelspace = cad.modelspace()
            cad.styles.new("epa2HydChart", dxfattribs={"font" : "Microsoft JhengHei"})

            return cad, msp
        except Exception as e:
            traceback.print_exc()

    def save_png(self, *args, **kwargs):
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
            return True
        except Exception as e:
            traceback.print_exc()
            return False

    def resetButton(self):
        self.MainWindow.l_block_size.setText(str(globals.BLOCK_SIZE_DEFAULT))
        self.MainWindow.l_joint_size.setText(str(globals.JOINT_SIZE_DEFAULT))
        self.MainWindow.l_text_size.setText(str(globals.TEXT_SIZE_DEFAULT))
        self.MainWindow.l_leader_distance.setText(str(globals.LEADER_DISTANCE_DEFAULT))
        self.MainWindow.l_line_width.setText(str(globals.LINE_WIDTH_DEFAULT))
        self.MainWindow.chk_export_0cmd.setChecked(True)
        self.MainWindow.chk_autoSize.setChecked(False)
        
        self.MainWindow.l_inp_path.setText('')
        self.MainWindow.l_rpt_path.setText('')
        self.MainWindow.l_projName.setText('')
        self.MainWindow.list_hrs.clear()
        globals.inpFile=None
        globals.rptFile=None
        globals.projName=None

    def processButton(self):
        try:
            globals.block_size=float(self.MainWindow.l_block_size.text())
            globals.joint_size=float(self.MainWindow.l_joint_size.text())
            globals.text_size=float(self.MainWindow.l_text_size.text())
            globals.line_width=float(self.MainWindow.l_line_width.text())
            globals.leader_distance=float(self.MainWindow.l_leader_distance.text())
        
            process1()
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
            flowDirectionArrowBlock.add_polyline2d([(0,0), (-1,0.4), (-1,-0.4)], close=True)
            flowDirectionArrowBlock.add_hatch().paths.add_polyline_path([(0,0), (-1,0.4), (-1,-0.4)], is_closed=True)

            from ezdxf.enums import TextEntityAlignment
            from ezdxf.math import Vec2
            pumpBlock=cad.blocks.new(name='pump')
            pumpBlock.add_circle(Vec2(0,0), 0.5)
            pumpBlock.add_text("P", height=0.8, dxfattribs={"style": "epa2HydChart"}).set_placement((0,0), align=TextEntityAlignment.MIDDLE_CENTER)
        except Exception as e:
            traceback.print_exc()

    def insertBlocks(self, *args, **kwargs):
        try:
            width=kwargs.get('width')
            mapping = {'tank': '水池',
                    'reservoir': '接水點',
                    'junction': '節點',
                    'pump': '抽水機',
                    'valve': '閥件'}

            df_mapping = {'tank': globals.df_Tanks,
                        'reservoir': globals.df_Reservoirs,
                        'junction': globals.df_Junctions,
                        'pump': globals.df_Pumps,
                        'valve': globals.df_Valves}
            for item in ['tank', 'reservoir', 'junction', 'pump', 'valve']:
                if item == 'valve':
                    import math
                    df=globals.df_Valves
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

                        globals.msp.add_blockref(item, [x,y], dxfattribs={'xscale':globals.block_size, 'yscale':globals.block_size, 'rotation':rotation})
                        globals.msp.add_polyline2d([(x1,y1), (x2,y2)], dxfattribs={'default_start_width': width, 'default_end_width': width})
                        msg= f'閥件 {id} 圖塊已插入'
                        log.renew_log(msg, False)
                        log.setLogToButton()
                        progress_utils.setProgress(ForcedValue=None)

                else:
                    df=df_mapping[item]
                    for i in range (0, len(df)):
                        id=df.at[i,'ID']
                        x=float(df.at[i,'x'])
                        y=float(df.at[i,'y'])
                        if item == 'junction':
                            globals.msp.add_blockref(item, [x,y], dxfattribs={'xscale':globals.joint_size, 'yscale':globals.joint_size})
                        else:
                            globals.msp.add_blockref(item, [x,y], dxfattribs={'xscale':globals.block_size, 'yscale':globals.block_size})
                        msg= f'{mapping[item]} {id} 圖塊已插入'
                        log.renew_log(msg, False)
                        log.setLogToButton()
                        progress_utils.setProgress(ForcedValue=None)

        except Exception as e:
            traceback.print_exc()
    
    def save_dxf(self, *args, **kwargs):
        dxfPath=kwargs.get('dxfPath')
        main_window_instance=kwargs.get('main_window_instance')
        while True:
            try:
                globals.cad.saveas(dxfPath)
                return True
                # break
            except:
                traceback.print_exc()
                from PyQt6.QtWidgets import QApplication, QMessageBox

                msg_box=QMessageBox(QApplication.activeWindow())
                msg_box.setIcon(QMessageBox.Icon.Critical)
                msg_box.setWindowTitle("錯誤")
                msg_box.setText(f'無法儲存 {dxfPath}，請關閉相關檔案後重試')
                retry_button = msg_box.addButton("重試", msg_box.ButtonRole.ActionRole)
                cancel_button = msg_box.addButton("取消", msg_box.ButtonRole.ActionRole)
                msg_box.exec()
                if msg_box.clickedButton() == retry_button:
                    continue
                elif msg_box.clickedButton() == cancel_button:
                    msg=f'[Error]無法儲存 {dxfPath}，中止匯出'
                    utils.renew_log(msg, True)
                    return

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
            return True
        except Exception as e:
            traceback.print_exc()
            return False

warnings.simplefilter(action='ignore', category=FutureWarning)
# QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)   # Enable high DPI
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())