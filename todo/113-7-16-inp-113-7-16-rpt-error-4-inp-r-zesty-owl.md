# 計劃：改用 Python EPANET 套件取代 .rpt 檔案解析

## Context

目前程式需要使用者同時提供 .inp 和 .rpt 兩個檔案。.rpt 解析有 `end_offset` 的 bug（`arrange_rpt_file` 移除空白行後偏移量不符），導致最後一條管線資料遺漏。

使用者改變方向：不讀取 .rpt，改用 Python EPANET 套件（`epyt`）直接執行水力模擬，從記憶體取得結果，徹底解決解析問題。

---

## 方案說明

使用 [`epyt`](https://pypi.org/project/epyt/)（EPyT - EPANET Python Toolkit），它是 EPANET 2.2 C 函式庫的薄包裝層，Windows 版本會自動包含 `epanet2.dll`。

### 資料對應
| 現有來源（.rpt） | epyt API | 說明 |
|---|---|---|
| `df_node_results['ID']` | `getNodeNameID()` | 節點 ID 字串列表 |
| `df_node_results['Demand']` | `getNodeActualDemand()` | 實際需水量 |
| `df_node_results['Head']` | `getNodeHydaulicHead()` | 水頭 (m) |
| `df_node_results['Pressure']` | `getNodePressure()` | 壓力 (m) |
| `df_link_results['ID']` | `getLinkNameID()` | 管線 ID 字串列表 |
| `df_link_results['Flow']` | `getLinkFlows()` | 流量（與 .inp Units 相同）|
| `df_link_results['Velocity']` | `getLinkVelocity()` | 流速 (m/s) |
| `df_link_results['unitHeadloss']` | `getLinkHeadloss()` | 單位水頭損失 (m/km，SI) |
| `df_link_results['Headloss']` | ← 由現有 `calculate_link_headloss()` 計算，無需改動 ||

> `getLinkHeadloss()` 在 EPANET C API 中回傳的就是 unit headloss (m/km for SI)，與 .rpt 格式一致。

---

## 需修改的檔案

### 1. `requirements.txt`
新增：
```
epyt
```

### 2. 新增 `epanet_runner.py`（全新檔案）

```python
"""Run EPANET simulation via epyt and return hydraulic results by time step."""
import pandas as pd
import traceback
import globals


def _seconds_to_hr_str(t_seconds):
    """Convert simulation time in seconds to 'H:MM' string."""
    hours = t_seconds // 3600
    minutes = (t_seconds % 3600) // 60
    return f"{hours}:{minutes:02d}"


def run_simulation(inp_file):
    """
    Run EPANET simulation from .inp file.

    Returns
    -------
    tuple: (simulation_results, hr_list)
        simulation_results: dict {hr_str: {'nodes': DataFrame, 'links': DataFrame}}
        hr_list: list of hr strings; [] if single time step (matches existing convention)
    """
    from epyt import epanet

    en = epanet(inp_file, display_msg=False)
    results = {}
    hr_list_internal = []

    try:
        en.openHydraulicAnalysis()
        en.initializeHydraulicAnalysis(0)  # 0 = EN_NOSAVE

        tstep = 1
        while tstep > 0:
            t = en.runHydraulicAnalysis()       # current time (seconds)
            hr_str = _seconds_to_hr_str(t)

            node_ids = en.getNodeNameID()
            link_ids = en.getLinkNameID()

            nodes_df = pd.DataFrame({
                'ID': node_ids,
                'Demand': en.getNodeActualDemand(),
                'Head': en.getNodeHydaulicHead(),
                'Pressure': en.getNodePressure(),
            })

            links_df = pd.DataFrame({
                'ID': link_ids,
                'Flow': en.getLinkFlows(),
                'Velocity': en.getLinkVelocity(),
                'unitHeadloss': en.getLinkHeadloss(),   # m/km for SI units
            })

            results[hr_str] = {'nodes': nodes_df, 'links': links_df}
            hr_list_internal.append(hr_str)

            tstep = en.nextHydraulicAnalysisStep()

        en.closeHydraulicAnalysis()

    except Exception as e:
        traceback.print_exc()
        globals.logger.exception(e)
        raise
    finally:
        en.unload()

    # Single time period: hr_list = [] to match existing convention
    if len(hr_list_internal) <= 1:
        return results, []
    else:
        return results, hr_list_internal
```

### 3. `globals.py`
新增一行：
```python
simulation_results = None  # Dict: {hr_str: {'nodes': df, 'links': df}}
```

### 4. `load_button.py`

**`handle_inp_file_selection()`**：載入 .inp 後立即執行模擬、填入 hr_list：

```python
def handle_inp_file_selection():
    import epanet_runner
    file, _ = QFileDialog.getOpenFileName(
        globals.main_window, '開啟inp檔', filter='inp (*.inp)')

    if file:
        globals.main_window.ui.l_inp_path.setText(os.path.basename(file))
        globals.inp_file = file
        globals.proj_name = os.path.splitext(os.path.basename(file))[0]
        globals.main_window.ui.l_projName.setText(globals.proj_name)

        globals.main_window.ui.list_hrs.clear()
        globals.main_window.ui.browser_log.append('執行EPANET水力分析...')
        message.set_message_to_button()

        try:
            simulation_results, hr_list = epanet_runner.run_simulation(file)
            globals.simulation_results = simulation_results
            globals.hr_list = hr_list

            if hr_list == []:
                globals.main_window.ui.list_hrs.addItems(['單一時段'])
                globals.main_window.ui.list_hrs.selectAll()
            else:
                globals.main_window.ui.list_hrs.addItems(hr_list)
                globals.main_window.ui.list_hrs.item(0).setSelected(True)

            globals.main_window.ui.browser_log.append('水力分析完成')
        except Exception as e:
            globals.main_window.ui.browser_log.append(f'[Error] 水力分析失敗: {str(e)}')
            message.set_message_to_button()

    elif globals.main_window.ui.l_inp_path.text():
        file = globals.main_window.ui.l_inp_path.text()
        globals.inp_file = file
        globals.proj_name = os.path.splitext(os.path.basename(file))[0]
        globals.main_window.ui.l_projName.setText(globals.proj_name)

    check_and_enable_autosize()
```

**`check_and_enable_autosize()`**：只需 .inp + 模擬結果即可：
```python
def check_and_enable_autosize():
    if globals.inp_file and globals.simulation_results:
        globals.main_window.ui.chk_autoSize.setEnabled(True)
    else:
        globals.main_window.ui.chk_autoSize.setEnabled(False)
```

### 5. `process_utils.py`：`process1()`

**將 .rpt 相關改為 simulation_results 查詢：**

```python
def process1():
    inp_file = globals.inp_file
    simulation_results = globals.simulation_results

    if inp_file and simulation_results:   # ← 原本是 "inp_file and rpt_file"
        output_dir = QFileDialog.getExistingDirectory(...)
        if output_dir:
            ...
            utils.load_inp_file_to_dataframe(inp_file, showtime=True)
            ...
            if globals.hr_list == []:  # 單一時段
                hr_key = next(iter(simulation_results))
                globals.df_node_results = simulation_results[hr_key]['nodes'].copy()
                globals.df_link_results = simulation_results[hr_key]['links'].copy()
                progress_utils.set_progress_bar(0)
                (globals.df_node_results, globals.df_junctions) = read_utils.change_value_by_digits(
                    digits=globals.digit_decimal)
                # 不再需要 verify_inp_rpt_files_match（模擬來自同一 .inp，必然相符）
                read_utils.calculate_link_headloss()
                process2(dxf_path=dxf_path, hr='')
                ...
            else:  # 多時段
                for h in hr_list_select:
                    globals.df_node_results = simulation_results[h]['nodes'].copy()
                    globals.df_link_results = simulation_results[h]['links'].copy()
                    progress_utils.set_progress_bar(0)
                    (globals.df_node_results, globals.df_junctions) = read_utils.change_value_by_digits(
                        digits=globals.digit_decimal)
                    read_utils.calculate_link_headloss()
                    process2(dxf_path=dxf_path, hr=h)
                    ...
```

> `verify_inp_rpt_files_match()` 可移除（結果由同一 .inp 產生，必然相符）。

---

## UI 考量（需確認）

- 原本的「開啟rpt檔」按鈕可隱藏或移除（需修改 `.ui` 檔案）
- 或先保留按鈕但不使用（不影響功能）
- `globals.rpt_file` 可保留但不再作為 `process1()` 的前提條件

---

## 驗證方式

1. `pip install epyt` 後重新執行程式
2. 只載入 `todo\水力分析113.7.16\水力分析113.7.16.inp`（不需要 .rpt）
3. 確認 hr_list 顯示 `0:00, 1:00, 2:00, 3:00`
4. 選擇時間段並產生 DXF
5. 確認 4 條管線全部有正確標示與流向箭頭
6. 確認 `log.txt` 無 `IndexError: list index out of range`

---

## 需注意事項

- epyt 在 Windows 上會自動尋找 `epanet2.dll`，需確認 PyInstaller 打包時能正確包含
- `epyt` 的 `getLinkHeadloss()` 回傳 unit headloss（m/km，SI），與 .rpt 格式一致
- `calculate_link_headloss()` 不需修改，仍從 node head 計算 total headloss
- `change_value_by_digits()` 已有 `astype(float)` 轉換，可接受 epyt 回傳的 float 值
