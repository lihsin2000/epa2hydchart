import globals
import traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def find_negative_low_pressure_junctions():
    """Find junctions with negative and low pressure conditions."""
    
    df_node_results = globals.df_node_results
    df_reservoirs = globals.df_reservoirs
    
    df = df_node_results[~df_node_results['ID'].isin(df_reservoirs['ID'])]
    df_nagaive_pressure = df[df['Pressure'].astype(
        float) < globals.nagaive_pressure_threshold]
    df_low_pressure_junctions = df[df['Pressure'].astype(
        float) < globals.low_pressure_threshold]
    return df_low_pressure_junctions, df_nagaive_pressure


def find_unreasonable_pipes():
    """Find pipes with unreasonable headloss or velocity characteristics."""
    
    df_link_results = globals.df_link_results
    df_pipes = globals.df_pipes
    df_pumps = globals.df_pumps
    df_valves = globals.df_valves
    
    links = df_link_results.copy()
    pipes = df_pipes
    pumps = df_pumps
    valves = df_valves
    links = links[~links['ID'].isin(pumps['ID'])]
    links = links[~links['ID'].isin(valves['ID'])]

    for index, row in links.iterrows():
        pipe_id = row['ID']
        Node1 = pipes.loc[pipes['ID'] == pipe_id, 'Node1'].values[0]
        Node2 = pipes.loc[pipes['ID'] == pipe_id, 'Node2'].values[0]
        diameter = pipes.loc[pipes['ID'] == pipe_id, 'Diameter'].values[0]
        Length = pipes.loc[pipes['ID'] == pipe_id, 'Length'].values[0]
        links.at[index, 'Node1'] = Node1
        links.at[index, 'Node2'] = Node2
        links.at[index, 'Diameter'] = diameter
        links.at[index, 'Length'] = Length
        # df.at[index , 'Reason']='Too high headloss (>|{:.2f}|)'.format(config.UNIT_HEADLOSS_THRESHOLD)

    # df=df.drop(columns=['index'])
    links = links.reset_index(drop=True)

    df_headloss_unreasonable = links[abs(links['unitHeadloss'].astype(
        float)) >= globals.unit_headloss_threshold].copy()

    for index, row in df_headloss_unreasonable.iterrows():
        unit_headloss = float(row['unitHeadloss'])
        diameter = float(row['Diameter'])
        if diameter >= 100:
            diameter_suggest = (
                (unit_headloss/globals.unit_headloss_threshold)*(diameter ** 4.8704)) ** (1/4.8704)
            diameter_suggest = 50*(int(diameter_suggest/50)+1)
            df_headloss_unreasonable.loc[index,
                                         'Diameter_suggest'] = f'{diameter_suggest:.0f}'

    df_velocity_unreasonable = links[abs(
        links['Velocity'].astype(float)) < globals.unit_velocity_threshold]
    df_velocity_unreasonable = links[(links['Diameter'].astype(int)) > 100]
    return df_headloss_unreasonable, df_velocity_unreasonable


def list_pipe_dimension():
    """List all unique pipe diameters and their counts."""
    import pandas as pd
    
    df_pipes = globals.df_pipes
    
    df = pd.DataFrame(columns=['Diameter', 'Amount'])
    pipes = df_pipes
    unique_diameters = pipes['Diameter'].unique().tolist()
    unique_diameters.sort()
    # unique_diameters=[int(x) for x in unique_diameters]
    for item in unique_diameters:
        pipe_amount_with_this_diameter = pipes[pipes['Diameter'] == item]
        new_row = {'Diameter': item, 'Amount': len(
            pipe_amount_with_this_diameter)}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df = df.reset_index(drop=True)
    return df


def write_report_header():
    """Write the header section of the analysis report."""
    import os

    if os.path.exists(f'{globals.output_folder}/report.txt'):
        os.remove(f'{globals.output_folder}/report.txt')

    with open(f'{globals.output_folder}/report.txt', 'a', encoding='utf-8') as f:
        f.write('Report\n\n')
        f.write(
            '----------------------------------------------------------------------\n\n')


def write_report_pipe_dimension(pipe_dimension):
    """Write pipe dimension statistics to the report file."""
    with open(f'{globals.output_folder}/report.txt', 'a', encoding='utf-8') as f:
        f.write('Static for pipe dimensions.\n\n')

        if pipe_dimension.empty:
            f.write('無\n\n')
        else:
            f.write(pipe_dimension.to_string(index=False))
            f.write('\n\n')

        f.write(
            '----------------------------------------------------------------------\n\n')


def write_report(headloss_unreasonable_pipes, velocity_unreasonable_pipes, low_pressure_junctions, nagaive_pressure, hr):
    """Write detailed analysis report including problematic pipes and junctions."""
    import os

    # headloss_unreasonable_pipes=kwargs.get('headloss_unreasonable_pipes', None)
    # velocity_unreasonable_pipes=kwargs.get('velocity_unreasonable_pipes', None)
    # nagavite_pressure_junctions=kwargs.get('nagavite_pressure_junctions', None)
    # hr=kwargs.get('hr', None)

    with open(f'{globals.output_folder}/report.txt', 'a', encoding='utf-8') as f:
        if hr:
            f.write(
                f'Unit Headloss >= {globals.unit_headloss_threshold} m/km in {hr}.\n\n')
        else:
            f.write(
                f'Unit Headloss >= {globals.unit_headloss_threshold} m/km.\n\n')

        if headloss_unreasonable_pipes.empty:
            f.write('無\n\n')
        else:
            f.write(headloss_unreasonable_pipes.to_string(index=False))
            f.write('\n\n')

        f.write(
            '----------------------------------------------------------------------\n\n')

        if hr:
            f.write(
                f'Velocity < {globals.unit_velocity_threshold} m/s in {hr}.\n\n')
        else:
            f.write(f'Velocity < {globals.unit_velocity_threshold} m/s.\n\n')

        if velocity_unreasonable_pipes.empty:
            f.write('無\n\n')
        else:
            f.write(velocity_unreasonable_pipes.to_string(index=False))
            f.write('\n\n')

        f.write(
            '----------------------------------------------------------------------\n\n')

        if hr:
            f.write(
                f'Pressure < {globals.low_pressure_threshold} m in {hr}.\n\n')
        else:
            f.write(f'Pressure < {globals.low_pressure_threshold} m.\n\n')

        if low_pressure_junctions.empty:
            f.write('無\n\n')
        else:
            f.write(low_pressure_junctions.to_string(index=False))
            f.write('\n\n')

        f.write(
            '----------------------------------------------------------------------\n\n')

        if hr:
            f.write(
                f'Negative Pressure < {globals.nagaive_pressure_threshold} m in {hr}.\n\n')
        else:
            f.write(
                f'Negative Pressure < {globals.nagaive_pressure_threshold} m.\n\n')

        if nagaive_pressure.empty:
            f.write('無\n\n')
        else:
            f.write(nagaive_pressure.to_string(index=False))
            f.write('\n\n')

        f.write(
            '----------------------------------------------------------------------\n\n')
