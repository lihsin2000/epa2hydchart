import config

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow

def calculateProgressSteps():
    # number steps for "insertBlocks"
    steps_insertBlocks = len(config.df_Tanks) + len(config.df_Reservoirs) + len(config.df_Junctions)+ len(config.df_Pumps) + len(config.df_Valves)

    # number steps for "insertPipeLines"
    steps_insertPipeLines = len(config.df_Pipes)

    # number steps for "insertPipeAnnotation"
    steps_insertPipeAnnotation = len(config.df_Pipes)

    # number steps for "insertDemandLeader"
    steps_insertDemandLeader = len(config.df_Junctions)

    # number steps for "insertHeadPressureLeader"
    steps_insertHeadPressureLeader = len(config.df_Junctions)

    # number steps for "insertReservoirsLeader"
    steps_insertReservoirsLeader = len(config.df_Reservoirs)

    # number steps for "insertTankLeader"
    steps_insertTankLeader = len(config.df_Tanks)

    # number steps for "insertPumpAnnotation"
    steps_insertPumpAnnotation = len(config.df_Pumps)

    # number steps for "insertValveAnnotation"
    steps_insertValveAnnotation = len(config.df_Valves)

    # numbers steps for exporting files
    steps_exportingFiles = 3  # dxf, svg, png

    total_steps = steps_insertBlocks + steps_insertPipeLines+ steps_insertPipeAnnotation \
                + steps_insertDemandLeader + steps_insertHeadPressureLeader \
                + steps_insertReservoirsLeader + steps_insertTankLeader \
                + steps_insertPumpAnnotation + steps_insertValveAnnotation \
                + steps_exportingFiles
    
    return total_steps

def setProgress(main_window_instance: 'MainWindow'):
    config.progress_value += config.progress_space
    value=int(config.progress_value)
    main_window_instance.MainWindow.progressBar.setValue(value)