import globals
from PyQt6.QtWidgets import QMainWindow, QApplication
import sys
import warnings
import traceback
import logging

# Suppress PyQt6 SIP deprecation warnings
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, message=".*sipPyTypeDict.*")

logging.basicConfig(level=logging.INFO, filename='log.txt', filemode='w', encoding='utf-8-sig')

class MainWindow(QMainWindow):
    def __init__(self):
        """
        Initialize the main window.
        """
        super(MainWindow, self).__init__()
        from ui import Ui_MainWindow

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set the main window instance in globals
        globals.main_window = self

        # Setup all UI elements, connections, and default values
        from ui_setup import setup_ui_elements
        setup_ui_elements()

    def create_modelspace(self):
        """
        Create and return a new DXF document and modelspace.

        Returns
        -------
        tuple
            (cad document, modelspace) if successful, (None, None) if failed.
        """
        try:
            import ezdxf
            cad = ezdxf.new()
            msp = cad.modelspace()
            cad.styles.new("epa2HydChart", dxfattribs={
                           "font": "Microsoft JhengHei"})

            return cad, msp
        except Exception as e:
            traceback.print_exc()
            globals.logger.exception(e)
            return None, None

    def reset_form_to_defaults(self):
        """
        Reset the UI form to default values.
        """
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
        """
        Start the processing workflow.
        """
        try:
            globals.block_size = float(self.ui.l_block_size.text())
            globals.joint_size = float(self.ui.l_joint_size.text())
            globals.text_size = float(self.ui.l_text_size.text())
            globals.line_width = float(self.ui.l_line_width.text())
            globals.leader_distance = float(self.ui.l_leader_distance.text())

            from process_utils import process1
            process1()
        except Exception as e:
            traceback.print_exc()
            globals.logger.exception(e)


warnings.simplefilter(action='ignore', category=FutureWarning)
# QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)   # Enable high DPI
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
