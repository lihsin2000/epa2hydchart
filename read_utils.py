import traceback
import pandas as pd
import globals
import utils
from PyQt6.QtWidgets import QMessageBox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def read_vertices(inpFile):
    try:
        start, end = utils.line_start_end(inpFile, '[VERTICES]', '[LABELS]', 2, 2)
        lines = open(inpFile).readlines()

        data = []
        for l in range(start-1, end):
            d = utils.parse_line_to_dictionary(lines=lines, l=l, position=2)
            data.append([d[0], float(d[1]), float(d[2])])
        df = pd.DataFrame(data, columns=['LINK', 'x', 'y'])
        return df
    except Exception as e:
        traceback.print_exc()


def read_pipes(inpFile):
    try:
        start, end = utils.line_start_end(inpFile, '[PIPES]', '[PUMPS]', 2, 2)
        lines = open(inpFile).readlines()

        data = []
        for l in range(start - 1, end):
            d = utils.parse_line_to_dictionary(lines=lines, l=l, position=4)
            data.append([d[1], d[2], d[3], d[4], d[5], d[6]])
        df = pd.DataFrame(
            data, columns=['ID', 'Node1', 'Node2', 'Length', 'Diameter', 'Roughness'])

        for i in range(0, len(df)):
            Node1 = df.at[i, 'Node1']
            row = globals.df_coords.index[globals.df_coords['ID'] == str(Node1)].tolist()[0]
            df.at[i, 'Node1_x'] = globals.df_coords.at[row, 'x']
            df.at[i, 'Node1_y'] = globals.df_coords.at[row, 'y']

            Node2 = df.at[i, 'Node2']
            row = globals.df_coords.index[globals.df_coords['ID'] == str(Node2)].tolist()[0]
            df.at[i, 'Node2_x'] = globals.df_coords.at[row, 'x']
            df.at[i, 'Node2_y'] = globals.df_coords.at[row, 'y']
        return df
    except Exception as e:
        traceback.print_exc()


def read_coords(inpFile):
    try:
        start, end = utils.line_start_end(inpFile, '[COORDINATES]', '[VERTICES]', 2, 2)
        lines = open(inpFile).readlines()
        df = pd.DataFrame(columns=['ID', 'x', 'y'])
        for l in range(start-1, end):
            d = utils.parse_line_to_dictionary(lines=lines, l=l, position=2)
            data = {
                'ID': d[0],
                'x': d[1],
                'y': d[2]
            }
            if df.empty:
                df.loc[0] = data
            else:
                df.loc[len(df)] = data
        df = df.reset_index(drop=True)
        return df
    except Exception as e:
        traceback.print_exc()


def read_junctions(inpFile):
    try:
        start, end = utils.line_start_end(inpFile, '[JUNCTIONS]', '[RESERVOIRS]', 2, 2)
        lines = open(inpFile).readlines()
        df = pd.DataFrame(columns=['ID', 'Elev', 'BaseDemand', 'x', 'y'])
        for l in range(start-1, end):
            d = utils.parse_line_to_dictionary(lines=lines, l=l, position=2)
            data = {
                'ID': d[1],
                'Elev': d[2],
                'BaseDemand': d[3]
            }
            if df.empty:
                df.loc[0] = data
            else:
                df.loc[len(df)] = data
        df = df.reset_index(drop=True)
        df = merge_coordinates_to_dataframe(df)
        return df
    except Exception as e:
        traceback.print_exc()


def read_reservoirs(inpFile):
    try:
        start, end = utils.line_start_end(inpFile, '[RESERVOIRS]', '[TANKS]', 2, 2)
        lines = open(inpFile).readlines()
        df = pd.DataFrame(columns=['ID', 'Head', 'x', 'y'])
        for l in range(start-1, end):
            d = utils.parse_line_to_dictionary(lines=lines, l=l, position=2)
            data = {
                'ID': d[1],
                'Head': d[2]
            }
            if df.empty:
                df.loc[0] = data
            else:
                df.loc[len(df)] = data
        df = df.reset_index(drop=True)
        df = merge_coordinates_to_dataframe(df)
        return df
    except Exception as e:
        traceback.print_exc()


def read_tanks(inpFile):
    try:
        start, end = utils.line_start_end(inpFile, '[TANKS]', '[PIPES]', 2, 2)
        lines = open(inpFile).readlines()
        df = pd.DataFrame(columns=['ID', 'Elev', 'MinLevel', 'MaxLevel', 'MinElev', 'MaxElev', 'x', 'y'])
        for l in range(start-1, end):
            d = utils.parse_line_to_dictionary(lines=lines, l=l, position=2)
            elev = float(d[2])
            min_level = float(d[4])
            max_level = float(d[5])
            min_elev = elev+min_level
            max_elev = elev+max_level
            data = {
                'ID': d[1],
                'Elev': elev,
                'MinLevel': min_level,
                'MaxLevel': max_level,
                'MinElev': min_elev,
                'MaxElev': max_elev
            }
            if df.empty:
                df.loc[0] = data
            else:
                df.loc[len(df)] = data
        df = df.reset_index(drop=True)
        df = merge_coordinates_to_dataframe(df)
        return df
    except Exception as e:
        traceback.print_exc()


def read_valves(inpFile):
    try:
        start, end = utils.line_start_end(inpFile, '[VALVES]', '[TAGS]', 2, 2)
        lines = open(inpFile).readlines()
        df = pd.DataFrame(columns=['ID', 'Node1', 'Node2', 'Node1_x', 'Node1_y', 'Node2_x', 'Node2_y', 'Type', 'Setting'])
        for l in range(start-1, end):
            d = utils.parse_line_to_dictionary(lines=lines, l=l, position=2)

            id = d[1]
            Node1 = d[2]
            Node2 = d[3]
            Type = d[5]
            Setting = d[6]
            coords1_row = globals.df_coords.index[globals.df_coords['ID'] == Node1].tolist()[0]
            coords2_row = globals.df_coords.index[globals.df_coords['ID'] == Node2].tolist()[0]
            Node1_x = globals.df_coords.at[coords1_row, 'x']
            Node1_y = globals.df_coords.at[coords1_row, 'y']
            Node2_x = globals.df_coords.at[coords2_row, 'x']
            Node2_y = globals.df_coords.at[coords2_row, 'y']

            data = {
                'ID': id,
                'Node1': Node1,
                'Node2': Node1,
                'Node1_x': Node1_x,
                'Node1_y': Node1_y,
                'Node2_x': Node2_x,
                'Node2_y': Node2_y,
                'Type': Type,
                'Setting': Setting
            }
            if df.empty:
                df.loc[0] = data
            else:
                df.loc[len(df)] = data
        df = df.reset_index(drop=True)
        return df
    except Exception as e:
        traceback.print_exc()


def read_pumps(inpFile):
    try:
        lines = open(inpFile).readlines()

        start_curve, end_curve = utils.line_start_end(inpFile, '[CURVES]', '[CONTROLS]', 2, 1)
        df_pump_curves = pd.DataFrame(columns=['ID', 'Q', 'H'])
        for l in range(start_curve-1, end_curve):
            if 'PUMP' in lines[l]:
                continue
            elif '\n' == lines[l]:
                continue
            else:
                d = utils.parse_line_to_dictionary(lines=lines, l=l, position=2)
                ID = d[1]
                Q = d[2]
                H = d[3]
            data_curve = {
                'ID': ID,
                'Q': Q,
                'H': H
            }
            if df_pump_curves.empty:
                df_pump_curves.loc[0] = data_curve
            else:
                df_pump_curves.loc[len(df_pump_curves)] = data_curve
        df_pump_curves = df_pump_curves.reset_index(drop=True)

        start, end = utils.line_start_end(inpFile, '[PUMPS]', '[VALVES]', 2, 2)
        df = pd.DataFrame(columns=['ID', 'Node1', 'Node2', 'Node1_x', 'Node1_y', 'Node2_x', 'Node2_y', 'x', 'y', 'Q', 'H'])
        for l in range(start-1, end):
            d = utils.parse_line_to_dictionary(lines=lines, l=l, position=2)
            ID = [d[1]][0]
            Node1 = [d[2]][0]
            Node2 = [d[3]][0]
            coords1_row = globals.df_coords.index[globals.df_coords['ID'] == Node1].tolist()[0]
            coords2_row = globals.df_coords.index[globals.df_coords['ID'] == Node2].tolist()[0]
            Node1_x = globals.df_coords.at[coords1_row, 'x']
            Node1_y = globals.df_coords.at[coords1_row, 'y']
            Node2_x = globals.df_coords.at[coords2_row, 'x']
            Node2_y = globals.df_coords.at[coords2_row, 'y']
            x = 0.5*(float(Node1_x)+float(Node2_x))
            y = 0.5*(float(Node1_y)+float(Node2_y))

            curve_id = d[5]
            i = int(df_pump_curves.index[df_pump_curves['ID'] == curve_id][0])
            Q = df_pump_curves.at[i, 'Q']
            H = df_pump_curves.at[i, 'H']

            data = {
                'ID': ID,
                'Node1': Node1,
                'Node2': Node2,
                'Node1_x': Node1_x,
                'Node1_y': Node1_y,
                'Node2_x': Node2_x,
                'Node2_y': Node2_y,
                'x': x,
                'y': y,
                'Q': Q,
                'H': H
            }
            if df.empty:
                df.loc[0] = data
            else:
                df.loc[len(df)] = data
        df = df.reset_index(drop=True)
        return df
    except Exception as e:
        traceback.print_exc()


def read_node_results(*args, **kwargs):
    try:
        hr = kwargs.get('hr')
        rpt_file = kwargs.get('input')

        if hr == None:
            start_str = 'Node Results:'
            end_str = 'Link Results:'
        else:
            start_str = f'Node Results at {hr} Hrs:'
            end_str = f'Link Results at {hr} Hrs:'
        start, end = utils.line_start_end(rpt_file, start_str, end_str, 5, 2)
        lines = open(rpt_file).readlines()
        df = pd.DataFrame(columns=['ID', 'Demand', 'Head', 'Pressure'])
        for l in range(start-1, end):
            d = utils.parse_line_to_dictionary(lines=lines, l=l, position=2)
            try:
                id = d[1]
                demand = d[2]
                head = d[3]
                pressure = d[4]

                data = {
                    'ID': id,
                    'Demand': demand,
                    'Head': head,
                    'Pressure': pressure,
                }

            except:
                globals.main_window.ui.browser_log.append(f'節點 {id} 資料錯誤，請手動修正.rpt檔內容')
                globals.any_error=True
                # QMessageBox.warning(None, '警告', f'節點{id}資料錯誤，請手動修正.rpt檔內容')

                data = {
                    'ID': id,
                    'Demand': None,
                    'Head': None,
                    'Pressure': None,
                }

            # if df.empty:
            #     df.loc[0] = data
            # else:
            df.loc[len(df)] = data
        df = df.reset_index(drop=True)
        return df
    except Exception as e:
        traceback.print_exc()


def read_link_results(*args, **kwargs):
    try:
        hr1 = kwargs.get('hr1')
        hr2 = kwargs.get('hr2')
        rpt_file = kwargs.get('input')
        digits= kwargs.get('digits')

        if hr1 == None:     # without patteren
            start_str = 'Link Results:'
            end_str = '[END]'
        elif hr2 == '':    # with patteren and last hour
            start_str = f'Link Results at {hr1} Hrs:'
            end_str = '[END]'
        elif hr1 != '' and hr2 != '':
            start_str = f'Link Results at {hr1} Hrs:'
            end_str = f'Node Results at {hr2} Hrs:'
        start, end = utils.line_start_end(rpt_file, start_str, end_str, 5, 2)
        lines = open(rpt_file).readlines()
        df = pd.DataFrame(columns=['ID', 'Flow', 'Velocity', 'unitHeadloss', 'Headloss'])
        for l in range(start-1, end):
            d = utils.parse_line_to_dictionary(lines=lines, l=l, position=2)
            pipe_id = d[1]
            flow = d[2]
            velocity = d[3]
            unit_headloss = d[4]

            # calculate headloss number:
            # 2 side in link are node:
            if pipe_id in globals.df_pipes['ID'].tolist():
                pipe_index = globals.df_pipes.index[globals.df_pipes['ID'] == pipe_id].tolist()[0]
                node1 = globals.df_pipes.at[pipe_index, 'Node1']
                i1 = globals.df_node_results.index[globals.df_node_results['ID'] == node1].tolist()[0]
                node2 = globals.df_pipes.at[pipe_index, 'Node2']
                i2 = globals.df_node_results.index[globals.df_node_results['ID'] == node2].tolist()[0]

                from decimal import Decimal
                try:
                    node1_head = Decimal(globals.df_node_results.at[i1, 'Head'])
                    node2_head = Decimal(globals.df_node_results.at[i2, 'Head'])

                    Headloss = round(abs(node2_head-node1_head), digits)
                    Headloss_str= f"{Headloss:.{digits}f}"

                except:
                    Headloss = 0
                    Headloss_str= f"{Headloss:.{digits}f}"


            data = {
                'ID': pipe_id,
                'Flow': flow,
                'Velocity': velocity,
                'unitHeadloss': unit_headloss,
                'Headloss': Headloss_str
            }
            if df.empty:
                df.loc[0] = data
            else:
                df.loc[len(df)] = data

        df = df.reset_index(drop=True)
        return df
    except Exception as e:
        traceback.print_exc()


def change_value_by_digits(*args, **kwargs):

    digits= kwargs.get('digits')
    
    try:
        df_nodeResult=globals.df_node_results
        df_junctions=globals.df_junctions

        df_nodeResult['Demand']=df_nodeResult['Demand'].astype(float)
        df_nodeResult['Head']=df_nodeResult['Head'].astype(float)
        df_junctions['Elev']=df_junctions['Elev'].astype(float)

        df_nodeResult['Demand'] = df_nodeResult['Demand'].map(lambda x: f"{x:.{digits}f}")
        df_nodeResult['Head'] = df_nodeResult['Head'].map(lambda x: f"{x:.{digits}f}")

        for index, row in df_nodeResult.iterrows():
            try:
                id= row['ID']
                head= float(row['Head'])
                elev= float(df_junctions.loc[df_junctions['ID'] == id, 'Elev'].values[0])
                pressure= head - elev
                df_nodeResult.at[index, 'Pressure'] = f"{pressure:.{digits}f}"
            except:
                continue

        df_junctions['Elev'] = df_junctions['Elev'].map(lambda x: f"{x:.{digits}f}")
                # df['Pressure'] = df['Pressure'].round(0)
        
        return (df_nodeResult, df_junctions)
    except Exception as e:
        traceback.print_exc()

def merge_coordinates_to_dataframe(df):
    '''
    從config.df_Coords讀取Tank, Reservoir的座標
    '''
    try:
        for i in range(0, len(df)):
            ID = df.at[i, 'ID']
            row = globals.df_coords.index[globals.df_coords['ID'] == str(ID)].tolist()[0]
            globals.df_coords['x'] = globals.df_coords['x'].astype(float)
            globals.df_coords['y'] = globals.df_coords['y'].astype(float)
            df.at[i, 'x'] = globals.df_coords.at[row, 'x']
            df.at[i, 'y'] = globals.df_coords.at[row, 'y']
        return df
    except Exception as e:
        traceback.print_exc()
