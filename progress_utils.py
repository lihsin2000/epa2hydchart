import globals

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow

def calculateProgressSteps():
    # number steps for "insertBlocks"
    steps_insertBlocks = len(globals.df_Tanks) + len(globals.df_Reservoirs) + len(globals.df_Junctions)+ len(globals.df_Pumps) + len(globals.df_Valves)

    # number steps for "insertPipeLines"
    steps_insertPipeLines = len(globals.df_Pipes)

    # number steps for "insertPipeAnnotation"
    steps_insertPipeAnnotation = len(globals.df_Pipes)

    # number steps for "insertDemandLeader"
    steps_insertDemandLeader = len(globals.df_Junctions)

    # number steps for "insertHeadPressureLeader"
    steps_insertHeadPressureLeader = len(globals.df_Junctions)

    # number steps for "insertReservoirsLeader"
    steps_insertReservoirsLeader = len(globals.df_Reservoirs)

    # number steps for "insertTankLeader"
    steps_insertTankLeader = len(globals.df_Tanks)

    # number steps for "insertPumpAnnotation"
    steps_insertPumpAnnotation = len(globals.df_Pumps)

    # number steps for "insertValveAnnotation"
    steps_insertValveAnnotation = len(globals.df_Valves)

    # numbers steps for exporting files
    steps_exportingFiles = 3  # dxf, svg, png

    total_steps = steps_insertBlocks + steps_insertPipeLines+ steps_insertPipeAnnotation \
                + steps_insertDemandLeader + steps_insertHeadPressureLeader \
                + steps_insertReservoirsLeader + steps_insertTankLeader \
                + steps_insertPumpAnnotation + steps_insertValveAnnotation \
                + steps_exportingFiles
    
    return total_steps

def setProgress():
    globals.progress_value += globals.progress_space
    value=int(globals.progress_value)
    globals.main_window.MainWindow.progressBar.setValue(value)
