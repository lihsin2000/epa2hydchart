import globals

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow

def calculate_progress_steps():
    # number steps for "insertBlocks"
    steps_insert_blocks = len(globals.df_tanks) + len(globals.df_reservoirs) + len(globals.df_junctions)+ len(globals.df_pumps) + len(globals.df_valves)

    # number steps for "insertPipeLines"
    steps_insert_pipe_lines = len(globals.df_pipes)

    # number steps for "insertDemandLeader"
    steps_insert_demand_leader = len(globals.df_junctions)

    # number steps for "insertHeadPressureLeader"
    steps_insert_head_pressure_leader = len(globals.df_junctions)

    # number steps for "insertReservoirsLeader"
    steps_insert_reservoirs_leader = len(globals.df_reservoirs)

    # number steps for "insertTankLeader"
    steps_insert_tank_leader = len(globals.df_tanks)

    # number steps for "insertPumpAnnotation"
    steps_insert_pump_annotation = len(globals.df_pumps)

    # number steps for "insertValveAnnotation"
    steps_insert_valve_annotation = len(globals.df_valves)

    # numbers steps for exporting files
    # steps_exportingFiles = 3  # dxf, svg, png

    total_steps = steps_insert_blocks + steps_insert_pipe_lines \
                + steps_insert_demand_leader + steps_insert_head_pressure_leader \
                + steps_insert_reservoirs_leader + steps_insert_tank_leader \
                + steps_insert_pump_annotation + steps_insert_valve_annotation \
    
    # print(f'steps_insertBlocks:{steps_insertBlocks}')
    # print(f'steps_insertPipeLines:{steps_insertPipeLines}')
    # print(f'steps_insertDemandLeader:{steps_insertDemandLeader}')
    # print(f'steps_insertHeadPressureLeader:{steps_insertHeadPressureLeader}')
    # print(f'steps_insertReservoirsLeader:{steps_insertReservoirsLeader}')
    # print(f'steps_insertTankLeader:{steps_insertTankLeader}')
    # print(f'steps_insertPumpAnnotation:{steps_insertPumpAnnotation}')
    # print(f'steps_insertValveAnnotation:{steps_insertValveAnnotation}')
    return total_steps

def set_progress(forced_value):
    if forced_value==None:
        globals.progress_value += globals.progress_space
        value=int(round(globals.progress_value,0))
        globals.main_window.ui.progressBar.setValue(value)
    else:
        globals.main_window.ui.progressBar.setValue(forced_value)
