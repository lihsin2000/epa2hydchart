import globals
from load_button import handle_inp_file_selection, handle_rpt_file_selection
from PyQt6.QtGui import QIntValidator, QDoubleValidator
import utils

def setup_ui_elements():
    """
    Configure all UI elements, button connections, and default values
    """
    # Button connections
    globals.main_window.ui.b_browser_inp.clicked.connect(lambda: handle_inp_file_selection())
    globals.main_window.ui.b_browser_rpt.clicked.connect(lambda: handle_rpt_file_selection())
    globals.main_window.ui.b_reset.clicked.connect(globals.main_window.reset_form_to_defaults)
    globals.main_window.ui.b_draw.clicked.connect(globals.main_window.start_processing)
    
    # Set default values and validators for input fields
    globals.main_window.ui.l_block_size.setText(str(globals.BLOCK_SIZE_DEFAULT))
    globals.main_window.ui.l_block_size.setValidator(QDoubleValidator())
    
    globals.main_window.ui.l_joint_size.setText(str(globals.JOINT_SIZE_DEFAULT))
    globals.main_window.ui.l_joint_size.setValidator(QDoubleValidator())
    
    globals.main_window.ui.l_text_size.setText(str(globals.TEXT_SIZE_DEFAULT))
    globals.main_window.ui.l_text_size.setValidator(QDoubleValidator())
    
    globals.main_window.ui.l_leader_distance.setText(str(globals.LEADER_DISTANCE_DEFAULT))
    globals.main_window.ui.l_leader_distance.setValidator(QIntValidator())
    
    globals.main_window.ui.l_line_width.setText(str(globals.LINE_WIDTH_DEFAULT))
    globals.main_window.ui.l_line_width.setValidator(QIntValidator())
    
    # Connect autoSize checkbox
    globals.main_window.ui.chk_autoSize.stateChanged.connect(lambda: utils.auto_size())
    
    # Set default combo box value
    globals.main_window.ui.comboBox_digits.setCurrentText('0.00')
