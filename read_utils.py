import traceback
import pandas as pd
import config
import utils
from PyQt6.QtWidgets import QMessageBox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main import MainWindow


def readVertices(inpFile):
    try:
        start, end = utils.lineStartEnd(inpFile, '[VERTICES]', '[LABELS]', 2, 2)
        lines = open(inpFile).readlines()

        data = []
        for l in range(start-1, end):
            d = utils.line2dict(lines, l)
            data.append([d[0], float(d[1]), float(d[2])])
        df = pd.DataFrame(data, columns=['LINK', 'x', 'y'])
        return df
    except Exception as e:
        traceback.print_exc()


def readPipes(inpFile):
    try:
        start, end = utils.lineStartEnd(inpFile, '[PIPES]', '[PUMPS]', 2, 2)
        lines = open(inpFile).readlines()

        data = []
        for l in range(start - 1, end):
            d = utils.line2dict(lines, l)
            data.append([d[1], d[2], d[3], d[4], d[5], d[6]])
        df = pd.DataFrame(
            data, columns=['ID', 'Node1', 'Node2', 'Length', 'Diameter', 'Roughness'])

        for i in range(0, len(df)):
            Node1 = df.at[i, 'Node1']
            row = config.df_Coords.index[config.df_Coords['ID'] == str(Node1)].tolist()[0]
            df.at[i, 'Node1_x'] = config.df_Coords.at[row, 'x']
            df.at[i, 'Node1_y'] = config.df_Coords.at[row, 'y']

            Node2 = df.at[i, 'Node2']
            row = config.df_Coords.index[config.df_Coords['ID'] == str(Node2)].tolist()[0]
            df.at[i, 'Node2_x'] = config.df_Coords.at[row, 'x']
            df.at[i, 'Node2_y'] = config.df_Coords.at[row, 'y']
        return df
    except Exception as e:
        traceback.print_exc()


def readCoords(inpFile):
    try:
        start, end = utils.lineStartEnd(inpFile, '[COORDINATES]', '[VERTICES]', 2, 2)
        lines = open(inpFile).readlines()
        df = pd.DataFrame(columns=['ID', 'x', 'y'])
        for l in range(start-1, end):
            d = utils.line2dict(lines, l)
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


def readJunctions(inpFile):
    try:
        start, end = utils.lineStartEnd(inpFile, '[JUNCTIONS]', '[RESERVOIRS]', 2, 2)
        lines = open(inpFile).readlines()
        df = pd.DataFrame(columns=['ID', 'Elev', 'BaseDemand', 'x', 'y'])
        for l in range(start-1, end):
            d = utils.line2dict(lines, l)
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
        df = appendCoords(df)
        return df
    except Exception as e:
        traceback.print_exc()


def readReservoirs(inpFile):
    try:
        start, end = utils.lineStartEnd(inpFile, '[RESERVOIRS]', '[TANKS]', 2, 2)
        lines = open(inpFile).readlines()
        df = pd.DataFrame(columns=['ID', 'Head', 'x', 'y'])
        for l in range(start-1, end):
            d = utils.line2dict(lines, l)
            data = {
                'ID': d[1],
                'Head': d[2]
            }
            if df.empty:
                df.loc[0] = data
            else:
                df.loc[len(df)] = data
        df = df.reset_index(drop=True)
        df = appendCoords(df)
        return df
    except Exception as e:
        traceback.print_exc()


def readTanks(inpFile):
    try:
        start, end = utils.lineStartEnd(inpFile, '[TANKS]', '[PIPES]', 2, 2)
        lines = open(inpFile).readlines()
        df = pd.DataFrame(columns=['ID', 'Elev', 'MinLevel', 'MaxLevel', 'MinElev', 'MaxElev', 'x', 'y'])
        for l in range(start-1, end):
            d = utils.line2dict(lines, l)
            elev = float(d[2])
            MinLevel = float(d[4])
            MaxLevel = float(d[5])
            MinElev = elev+MinLevel
            MaxElev = elev+MaxLevel
            data = {
                'ID': d[1],
                'Elev': elev,
                'MinLevel': MinLevel,
                'MaxLevel': MaxLevel,
                'MinElev': MinElev,
                'MaxElev': MaxElev
            }
            if df.empty:
                df.loc[0] = data
            else:
                df.loc[len(df)] = data
        df = df.reset_index(drop=True)
        df = appendCoords(df)
        return df
    except Exception as e:
        traceback.print_exc()


def readValves(inpFile):
    try:
        start, end = utils.lineStartEnd(inpFile, '[VALVES]', '[TAGS]', 2, 2)
        lines = open(inpFile).readlines()
        df = pd.DataFrame(columns=['ID', 'Node1', 'Node2', 'Node1_x', 'Node1_y', 'Node2_x', 'Node2_y', 'Type', 'Setting'])
        for l in range(start-1, end):
            d = utils.line2dict(lines, l)

            id = d[1]
            Node1 = d[2]
            Node2 = d[3]
            Type = d[5]
            Setting = d[6]
            coords1_row = config.df_Coords.index[config.df_Coords['ID'] == Node1].tolist()[0]
            coords2_row = config.df_Coords.index[config.df_Coords['ID'] == Node2].tolist()[0]
            Node1_x = config.df_Coords.at[coords1_row, 'x']
            Node1_y = config.df_Coords.at[coords1_row, 'y']
            Node2_x = config.df_Coords.at[coords2_row, 'x']
            Node2_y = config.df_Coords.at[coords2_row, 'y']

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


def readPumps(inpFile):
    try:
        lines = open(inpFile).readlines()

        start_curve, end_curve = utils.lineStartEnd(inpFile, '[CURVES]', '[CONTROLS]', 2, 1)
        df_pumpCurves = pd.DataFrame(columns=['ID', 'Q', 'H'])
        for l in range(start_curve-1, end_curve):
            if 'PUMP' in lines[l]:
                continue
            elif '\n' == lines[l]:
                continue
            else:
                d = utils.line2dict(lines, l)
                ID = d[1]
                Q = d[2]
                H = d[3]
            data_curve = {
                'ID': ID,
                'Q': Q,
                'H': H
            }
            if df_pumpCurves.empty:
                df_pumpCurves.loc[0] = data_curve
            else:
                df_pumpCurves.loc[len(df_pumpCurves)] = data_curve
        df_pumpCurves = df_pumpCurves.reset_index(drop=True)

        start, end = utils.lineStartEnd(inpFile, '[PUMPS]', '[VALVES]', 2, 2)
        df = pd.DataFrame(columns=['ID', 'Node1', 'Node2', 'Node1_x', 'Node1_y', 'Node2_x', 'Node2_y', 'x', 'y', 'Q', 'H'])
        for l in range(start-1, end):
            d = utils.line2dict(lines, l)
            ID = [d[1]][0]
            Node1 = [d[2]][0]
            Node2 = [d[3]][0]
            coords1_row = config.df_Coords.index[config.df_Coords['ID'] == Node1].tolist()[0]
            coords2_row = config.df_Coords.index[config.df_Coords['ID'] == Node2].tolist()[0]
            Node1_x = config.df_Coords.at[coords1_row, 'x']
            Node1_y = config.df_Coords.at[coords1_row, 'y']
            Node2_x = config.df_Coords.at[coords2_row, 'x']
            Node2_y = config.df_Coords.at[coords2_row, 'y']
            x = 0.5*(float(Node1_x)+float(Node2_x))
            y = 0.5*(float(Node1_y)+float(Node2_y))

            curveID = d[5]
            i = int(df_pumpCurves.index[df_pumpCurves['ID'] == curveID][0])
            Q = df_pumpCurves.at[i, 'Q']
            H = df_pumpCurves.at[i, 'H']

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


def readNodeResults(*args, **kwargs):
    try:
        hr = kwargs.get('hr')
        rptFile = kwargs.get('input')

        if hr == None:
            start_str = 'Node Results:'
            end_str = 'Link Results:'
        else:
            start_str = f'Node Results at {hr} Hrs:'
            end_str = f'Link Results at {hr} Hrs:'
        start, end = utils.lineStartEnd(rptFile, start_str, end_str, 5, 2)
        lines = open(rptFile).readlines()
        df = pd.DataFrame(columns=['ID', 'Demand', 'Head', 'Pressure'])
        for l in range(start-1, end):
            d = utils.line2dict(lines, l)
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
                MainWindow.MainWindow.browser_log.append(MainWindow.setLogToButton())
                QMessageBox.warning(None, '警告', f'節點{id}資料錯誤，請手動修正.rpt檔內容')

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


def readLinkResults(*args, **kwargs):
    try:
        hr1 = kwargs.get('hr1')
        hr2 = kwargs.get('hr2')
        rptFile = kwargs.get('input')
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
        start, end = utils.lineStartEnd(rptFile, start_str, end_str, 5, 2)
        lines = open(rptFile).readlines()
        df = pd.DataFrame(columns=['ID', 'Flow', 'Velocity', 'unitHeadloss', 'Headloss'])
        for l in range(start-1, end):
            d = utils.line2dict(lines, l)
            pipe_id = d[1]
            flow = d[2]
            velocity = d[3]
            unitHeadloss = d[4]

            # calculate headloss number:
            # 2 side in link are node:
            if pipe_id in config.df_Pipes['ID'].tolist():
                pipe_index = config.df_Pipes.index[config.df_Pipes['ID'] == pipe_id].tolist()[0]
                node1 = config.df_Pipes.at[pipe_index, 'Node1']
                i1 = config.df_NodeResults.index[config.df_NodeResults['ID'] == node1].tolist()[0]
                node2 = config.df_Pipes.at[pipe_index, 'Node2']
                i2 = config.df_NodeResults.index[config.df_NodeResults['ID'] == node2].tolist()[0]

                from decimal import Decimal
                try:
                    node1_head = Decimal(config.df_NodeResults.at[i1, 'Head'])
                    node2_head = Decimal(config.df_NodeResults.at[i2, 'Head'])

                    Headloss = round(abs(node2_head-node1_head), digits)
                    Headloss_str= f"{Headloss:.{digits}f}"

                except:
                    Headloss = 0
                    Headloss_str= f"{Headloss:.{digits}f}"


            data = {
                'ID': pipe_id,
                'Flow': flow,
                'Velocity': velocity,
                'unitHeadloss': unitHeadloss,
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


def changeValueByDigits(*args, **kwargs):

    digits= kwargs.get('digits')
    
    try:
        df_nodeResult=config.df_NodeResults
        df_junctions=config.df_Junctions

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

def appendCoords(df):
    '''
    從config.df_Coords讀取Tank, Reservoir的座標
    '''
    try:
        for i in range(0, len(df)):
            ID = df.at[i, 'ID']
            row = config.df_Coords.index[config.df_Coords['ID'] == str(ID)].tolist()[0]
            config.df_Coords['x'] = config.df_Coords['x'].astype(float)
            config.df_Coords['y'] = config.df_Coords['y'].astype(float)
            df.at[i, 'x'] = config.df_Coords.at[row, 'x']
            df.at[i, 'y'] = config.df_Coords.at[row, 'y']
        return df
    except Exception as e:
        traceback.print_exc()
