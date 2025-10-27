import sys
import warnings
import traceback

# Suppress PyQt6 SIP deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")

from PyQt6.QtWidgets import QMainWindow, QApplication

import globals

# Lazy imports - only import when needed
def lazy_import_ui():
    from ui import Ui_MainWindow
    return Ui_MainWindow

def lazy_import_setup():
    from ui_setup import setup_ui_elements
    return setup_ui_elements

def lazy_import_process():
    from process_utils import process1
    return process1

def lazy_import_ezdxf():
    import ezdxf
    from ezdxf.document import Drawing
    from ezdxf.layouts import Modelspace
    return ezdxf, Drawing, Modelspace

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        ui_main_window_class = lazy_import_ui()
        self.ui = ui_main_window_class()
        self.ui.setupUi(self)
        
        # Set the main window instance in globals
        globals.main_window = self
        
        # Setup all UI elements, connections, and default values
        setup_ui_elements = lazy_import_setup()
        setup_ui_elements()
        
    def create_modelspace(self, *args, **kwargs):
        try:
            ezdxf, Drawing, Modelspace = lazy_import_ezdxf()
            cad: Drawing = ezdxf.new()
            msp: Modelspace = cad.modelspace()
            cad.styles.new("epa2HydChart", dxfattribs={"font": "Microsoft JhengHei"})

            return cad, msp
        except Exception as e:
            traceback.print_exc()

    def reset_form_to_defaults(self):
        self.ui.l_block_size.setText(str(globals.BLOCK_SIZE_DEFAULT))
        self.ui.l_joint_size.setText(str(globals.JOINT_SIZE_DEFAULT))
        self.ui.l_text_size.setText(str(globals.TEXT_SIZE_DEFAULT))
        self.ui.l_leader_distance.setText(str(globals.LEADER_DISTANCE_DEFAULT))
        self.ui.l_line_width.setText(str(globals.LINE_WIDTH_DEFAULT))
        self.ui.chk_export_0cmd.setChecked(False)
        self.ui.chk_autoSize.setChecked(False)
        self.ui.chk_autoLabelPost.setChecked(False)
        
        self.ui.l_inp_path.setText('')
        self.ui.l_rpt_path.setText('')
        self.ui.l_projName.setText('')
        self.ui.list_hrs.clear()
        globals.inp_file = None
        globals.rpt_file = None
        globals.proj_name = None

    def start_processing(self):
        try:
            globals.block_size = float(self.ui.l_block_size.text())
            globals.joint_size = float(self.ui.l_joint_size.text())
            globals.text_size = float(self.ui.l_text_size.text())
            globals.line_width = float(self.ui.l_line_width.text())
            globals.leader_distance = float(self.ui.l_leader_distance.text())
        
            process1 = lazy_import_process()
            process1()
        except Exception as e:
            traceback.print_exc()

warnings.simplefilter(action='ignore', category=FutureWarning)
# QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)   # Enable high DPI
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
