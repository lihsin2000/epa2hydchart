import pandas as pd
import globals
import traceback

def check_negative_low_pressure_junctions(*args, **kwargs):
    df= globals.df_NodeResults
    reservoirs=globals.df_Reservoirs
    df=df[~df['ID'].isin(reservoirs['ID'])]
    df_nagavite_pressure = df[df['Pressure'].astype(float)<globals.NAGAVITE_PRESSURE_THRESHOLD]
    df_low_pressure_junctions = df[df['Pressure'].astype(float)<globals.LOW_PRESSURE_THRESHOLD]
    return df_low_pressure_junctions, df_nagavite_pressure


def filter_unreasonable_pipes(*args, **kwargs):
    df= globals.df_LinkResults
    pipes=globals.df_Pipes
    pumps= globals.df_Pumps
    valves= globals.df_Valves
    df=df[~df['ID'].isin(pumps['ID'])]
    df=df[~df['ID'].isin(valves['ID'])]

    for index, row in df.iterrows():
        pipe_id=row['ID']
        Node1=pipes.loc[pipes['ID']==pipe_id, 'Node1'].values[0]
        Node2=pipes.loc[pipes['ID']==pipe_id, 'Node2'].values[0]
        Diameter=pipes.loc[pipes['ID']==pipe_id, 'Diameter'].values[0]
        Length=pipes.loc[pipes['ID']==pipe_id, 'Length'].values[0]
        df.at[index , 'Node1']=Node1
        df.at[index , 'Node2']=Node2
        df.at[index , 'Diameter']=Diameter
        df.at[index , 'Length']=Length
        # df.at[index , 'Reason']='Too high headloss (>|{:.2f}|)'.format(config.UNIT_HEADLOSS_THRESHOLD)
    
    # df=df.drop(columns=['index'])
    df=df.reset_index(drop=True)

    df_headloss_unreasonable = df[abs(df['unitHeadloss'].astype(float))>=globals.UNIT_HEADLOSS_THRESHOLD].copy()

    for index, row in df_headloss_unreasonable.iterrows():
        unitHeadloss=float(row['unitHeadloss'])
        Diameter=float(row['Diameter'])
        if Diameter >=100:
            Diameter_suggest=((unitHeadloss/globals.UNIT_HEADLOSS_THRESHOLD)*(Diameter ** 4.8704)) ** (1/4.8704)
            Diameter_suggest=50*(int(Diameter_suggest/50)+1)
            df_headloss_unreasonable.loc[index , 'Diameter_suggest']=f'{Diameter_suggest:.0f}'
        pass

    df_velocity_unreasonable = df[abs(df['Velocity'].astype(float))<globals.UNIT_VELOCITY_THRESHOLD]
    df_velocity_unreasonable = df[(df['Diameter'].astype(int))>100]
    return df_headloss_unreasonable, df_velocity_unreasonable

def list_pipe_dimension(*args, **kwargs):
    df=pd.DataFrame(columns=['Diameter', 'Amount'])
    pipes=globals.df_Pipes
    unique_diameters=pipes['Diameter'].unique().tolist()
    unique_diameters.sort()
    # unique_diameters=[int(x) for x in unique_diameters]
    for item in unique_diameters:
        pipe_amount_with_this_diameter=pipes[pipes['Diameter']==item]
        new_row={'Diameter':item, 'Amount':len(pipe_amount_with_this_diameter)}
        df=pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df=df.reset_index(drop=True)
    return df

def write_report_header(*args, **kwargs):
    import os
    # hr=kwargs.get('hr', None)

    if os.path.exists(f'{globals.output_folder}/report.txt'):
        os.remove(f'{globals.output_folder}/report.txt')

    with open(f'{globals.output_folder}/report.txt', 'a', encoding='utf-8') as f:
        f.write('Report\n\n')
        f.write('----------------------------------------------------------------------\n\n')

def write_report_pipe_dimension(*args, **kwargs):
    pipe_dimension=kwargs.get('pipe_dimension')

    with open(f'{globals.output_folder}/report.txt', 'a', encoding='utf-8') as f:
        f.write('Static for pipe dimensions.\n\n')

        if pipe_dimension.empty:
            f.write('無\n\n')
        else:
            f.write(pipe_dimension.to_string(index=False))
            f.write('\n\n')

        f.write('----------------------------------------------------------------------\n\n')

def write_report(headloss_unreasonable_pipes, velocity_unreasonable_pipes, low_pressure_junctions, nagavite_pressure, hr):
    import os
    
    # headloss_unreasonable_pipes=kwargs.get('headloss_unreasonable_pipes', None)
    # velocity_unreasonable_pipes=kwargs.get('velocity_unreasonable_pipes', None)
    # nagavite_pressure_junctions=kwargs.get('nagavite_pressure_junctions', None)
    # hr=kwargs.get('hr', None)

    with open(f'{globals.output_folder}/report.txt', 'a', encoding='utf-8') as f:
        if hr:
            f.write(f'Unit Headloss >= {globals.UNIT_HEADLOSS_THRESHOLD} m/km in {hr}.\n\n')
        else:
            f.write(f'Unit Headloss >= {globals.UNIT_HEADLOSS_THRESHOLD} m/km.\n\n')

        if headloss_unreasonable_pipes.empty:
            f.write('無\n\n')
        else:
            f.write(headloss_unreasonable_pipes.to_string(index=False))
            f.write('\n\n')

        f.write('----------------------------------------------------------------------\n\n')

        if hr:
            f.write(f'Velocity < {globals.UNIT_VELOCITY_THRESHOLD} m/s in {hr}.\n\n')
        else:
            f.write(f'Velocity < {globals.UNIT_VELOCITY_THRESHOLD} m/s.\n\n')

        if velocity_unreasonable_pipes.empty:
            f.write('無\n\n')
        else:
            f.write(velocity_unreasonable_pipes.to_string(index=False))
            f.write('\n\n')

        f.write('----------------------------------------------------------------------\n\n')

        if hr:
            f.write(f'Pressure < {globals.LOW_PRESSURE_THRESHOLD} m in {hr}.\n\n')
        else:
            f.write(f'Pressure < {globals.LOW_PRESSURE_THRESHOLD} m.\n\n')

        if low_pressure_junctions.empty:
            f.write('無\n\n')
        else:
            f.write(low_pressure_junctions.to_string(index=False))
            f.write('\n\n')

        f.write('----------------------------------------------------------------------\n\n')

        if hr:
            f.write(f'Negative Pressure < {globals.NAGAVITE_PRESSURE_THRESHOLD} m in {hr}.\n\n')
        else:
            f.write(f'Negative Pressure < {globals.NAGAVITE_PRESSURE_THRESHOLD} m.\n\n')

        if nagavite_pressure.empty:
            f.write('無\n\n')
        else:
            f.write(nagavite_pressure.to_string(index=False))
            f.write('\n\n')

        f.write('----------------------------------------------------------------------\n\n')
