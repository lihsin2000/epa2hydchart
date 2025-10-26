import globals

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow

def calculate_progress_steps():
    # number steps for "insertBlocks"
    steps_insertBlocks = len(globals.df_Tanks) + len(globals.df_Reservoirs) + len(globals.df_Junctions)+ len(globals.df_Pumps) + len(globals.df_Valves)

    # number steps for "insertPipeLines"
    steps_insertPipeLines = len(globals.df_Pipes)

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
    # steps_exportingFiles = 3  # dxf, svg, png

    total_steps = steps_insertBlocks + steps_insertPipeLines \
                + steps_insertDemandLeader + steps_insertHeadPressureLeader \
                + steps_insertReservoirsLeader + steps_insertTankLeader \
                + steps_insertPumpAnnotation + steps_insertValveAnnotation \
    
    # print(f'steps_insertBlocks:{steps_insertBlocks}')
    # print(f'steps_insertPipeLines:{steps_insertPipeLines}')
    # print(f'steps_insertDemandLeader:{steps_insertDemandLeader}')
    # print(f'steps_insertHeadPressureLeader:{steps_insertHeadPressureLeader}')
    # print(f'steps_insertReservoirsLeader:{steps_insertReservoirsLeader}')
    # print(f'steps_insertTankLeader:{steps_insertTankLeader}')
    # print(f'steps_insertPumpAnnotation:{steps_insertPumpAnnotation}')
    # print(f'steps_insertValveAnnotation:{steps_insertValveAnnotation}')
    return total_steps

def set_progress(ForcedValue):
    if ForcedValue==None:
        globals.progress_value += globals.progress_space
        value=int(round(globals.progress_value,0))
        globals.main_window.MainWindow.progressBar.setValue(value)
    else:
        globals.main_window.MainWindow.progressBar.setValue(ForcedValue)
