import pandas as pd
import config

def filter_headloss_unreasonable_pipes(*args, **kwargs):
    link_results= config.df_LinkResults
    pipes=config.df_Pipes
    pumps= config.df_Pumps
    valves= config.df_Valves
    df = link_results[abs(link_results['unitHeadloss'].astype(float))>=config.UNIT_HEADLOSS_THRESHOLD]

    # remove pumps and valves from unreasonable_pipes
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
    return df

def filter_velocity_unreasonable_pipes(*args, **kwargs):
    df = config.df_LinkResults
    pipes=config.df_Pipes

    for index, row in df.iterrows():
        pipe_id=row['ID']
        Node1=pipes.loc[pipes['ID']==pipe_id, 'Node1'].values[0]
        Diameter=pipes.loc[pipes['ID']==pipe_id, 'Diameter'].values[0]
        Node2=pipes.loc[pipes['ID']==pipe_id, 'Node2'].values[0]
        Length=pipes.loc[pipes['ID']==pipe_id, 'Length'].values[0]
        df.at[index , 'Node1']=Node1
        df.at[index , 'Node2']=Node2
        df.at[index , 'Diameter']=Diameter
        df.at[index , 'Length']=Length
        # df.at[index , 'Reason']='Too Low velocity (<|{:.2f}|)'.format(config.UNIT_VELOCITY_THRESHOLD)
    
    df = df[abs(df['Velocity'].astype(float))<config.UNIT_VELOCITY_THRESHOLD]
    df = df[(df['Diameter'].astype(int))>100]
    
    # df=df.drop(columns=['index'])
    df=df.reset_index(drop=True)
    return df

def list_pipe_dimension(*args, **kwargs):
    df=pd.DataFrame(columns=['Diameter', 'Amount'])
    pipes=config.df_Pipes
    unique_diameters=pipes['Diameter'].unique().tolist()
    unique_diameters.sort()
    # unique_diameters=[int(x) for x in unique_diameters]
    for item in unique_diameters:
        pipe_amount_with_this_diameter=pipes[pipes['Diameter']==item]
        new_row={'Diameter':item, 'Amount':len(pipe_amount_with_this_diameter)}
        df=pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    df=df.reset_index(drop=True)
    return df

def write_report(*args, **kwargs):
    import os
    headloss_unreasonable_pipes=kwargs.get('headloss_unreasonable_pipes')
    pipe_dimension=kwargs.get('pipe_dimension')
    velocity_unreasonable_pipes=kwargs.get('velocity_unreasonable_pipes')

    if os.path.exists(f'{config.output_folder}/report.txt'):
        os.remove(f'{config.output_folder}/report.txt')

    with open(f'{config.output_folder}/report.txt', 'a', encoding='utf-8') as f:
        f.write('\n\n')
        f.write('Result\n\n')
        f.write('----------------------------------------------------------------------\n\n')

        f.write(f'1. Unit Headloss >= {config.UNIT_HEADLOSS_THRESHOLD} m/km.\n')
        if headloss_unreasonable_pipes.empty:
            f.write('無\n\n')
        else:
            f.write(headloss_unreasonable_pipes.to_string(index=False))
            f.write('\n\n')

        f.write('----------------------------------------------------------------------\n\n')

        f.write('2. Static for pipe dimentions.\n')
        if pipe_dimension.empty:
            f.write('無\n\n')
        else:
            f.write(pipe_dimension.to_string(index=False))
            f.write('\n\n')

        f.write('----------------------------------------------------------------------\n\n')

        f.write(f'3. Velocity < {config.UNIT_VELOCITY_THRESHOLD} m/s and Diameter > 100 mm.\n')
        if velocity_unreasonable_pipes.empty:
            f.write('無\n\n')
        else:
            f.write(velocity_unreasonable_pipes.to_string(index=False))
            f.write('\n\n')

        f.write('----------------------------------------------------------------------\n\n')