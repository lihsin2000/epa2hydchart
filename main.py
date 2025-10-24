
import ezdxf
from ezdxf.document import Drawing
from ezdxf.layouts import Modelspace
import sys, warnings, traceback

# Suppress PyQt6 SIP deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")

from ui import Ui_MainWindow
from PyQt6.QtWidgets import QMainWindow, QApplication

import globals
from process_utils import process1
from ui_setup import setup_ui_elements

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.MainWindow = Ui_MainWindow()
        self.MainWindow.setupUi(self)
        
        # Set the main window instance in globals
        globals.main_window = self
        
        # Setup all UI elements, connections, and default values
        setup_ui_elements()
        
    def createModelspace(self, *args, **kwargs):
        try:
            cad: Drawing = ezdxf.new()
            msp: Modelspace = cad.modelspace()
            cad.styles.new("epa2HydChart", dxfattribs={"font" : "Microsoft JhengHei"})

            return cad, msp
        except Exception as e:
            traceback.print_exc()

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

warnings.simplefilter(action='ignore', category=FutureWarning)
# QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)   # Enable high DPI
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
