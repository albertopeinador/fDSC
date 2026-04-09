import streamlit as st
import matplotlib.pyplot as plt
import Assets.new_file_loader as ld
import Assets.find_and_int as fai
import numpy as np
import Assets.new_scalebar as sc
import pandas as pd
from scipy.signal import savgol_filter
import plotly.graph_objects as go
import plotly.express as px
from matplotlib.colors import rgb2hex
from io import StringIO
import warnings

warnings.filterwarnings("ignore")

def bigdata_to_csv(data_dict, selected_cols):
    # List to hold all DataFrames after renaming
    renamed_dfs = []

    # Process each dictionary entry
    for key, (df1, df2) in data_dict.items():
        # Rename columns with dictionary key prefix to avoid conflicts
        filter_df1 = df1[selected_cols]
        filter_df2 = df2[selected_cols]
        filter_df1 = filter_df1.add_prefix(f"{key}_")
        filter_df2 = filter_df2.add_prefix(f"{key}_").add_suffix("_ref")

        # Store in list for final concatenation
        renamed_dfs.append(filter_df1)
        renamed_dfs.append(filter_df2)

    # Concatenate all DataFrames horizontally (axis=1)
    final_df = pd.concat(renamed_dfs, axis=1)

    new_order = []
    group_size = len(selected_cols)
    for i in range(0, len(final_df.columns), group_size):
        group = list(final_df.columns[i:i+group_size])
        # st.write(group)
        reordered = sorted(group, key=lambda col: 'Heat Flow' in col)
        new_order.extend(reordered)

    final_df = final_df[new_order]
    final_df_copy = final_df

    # Convert final DataFrame to CSV format
    output = StringIO()
    final_df.to_csv(output, index=False)

    # Get CSV content
    csv_string = output.getvalue()
    output.close()
    return csv_string

#  Set layout to wide screen
#st.set_page_config(layout="wide")

def common_substrings(strings):
    if not strings:
        return []
    
    shortest = min(strings, key=len)
    substrings = {shortest[i:j] for i in range(len(shortest)) for j in range(i+1, len(shortest)+1)}
    common = {s for s in substrings if all(s in string for string in strings)}
    maximal = {s for s in common if not any(s in other for other in common if s != other)}
    
    return sorted(maximal, key=lambda s: strings[0].index(s))


def annealings():
    #   Define text style for 'Enter folder name' text
    st.markdown(
        """
    <style>
    .big-font {
        font-size:30px !important;
        text-align:center !important;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # fig_dpi = 10

    config = {"toImageButtonOptions": {"height": None, "width": None, "format": "svg"}}


    #   Define figures and axis for the plots

    fig = go.Figure()

    #   Create the three main columns - one for main controls, one for the plots
    #       and one last one for the integrals plot and some adicional controls

    ctr_panel, graf, inte = st.columns([3, 4, 4])

    #   Set some of the controls from the first column. load_cutoff is position of first data point to load,
    #       margin_step is a percent of separation between curves, int_dif_th is threshold for integration,
    #       rest are self-explanatory

    with ctr_panel:
        with st.expander("Load controls", expanded=True):
            files = st.file_uploader(
                "Upload files",
                accept_multiple_files=True,
                type=["txt"],
                label_visibility="collapsed",
            )

            eje_x = st.selectbox("x axis", ["Tr", "Ts", "t"])

            load_start, load_end = st.columns(2)
            if eje_x == "t":
                with load_start:
                    load_begin = st.number_input(
                        "Start at " + eje_x, value=0.006, step=0.001, format="%.3f"
                    )
                with load_end:
                    load_fin = st.number_input(
                        "End at " + eje_x, value=0.260, step=0.001, format="%.3f"
                    )
            else:
                with load_start:
                    load_begin = st.number_input(
                        "Start at " + eje_x, value=-67.0, format="%.1f"
                    )
                with load_end:
                    load_fin = st.number_input(
                        "End at " + eje_x, value=425.0, format="%.1f"
                    )

            int_dif_th = 0.0
            scalebar_scale = st.slider(
                "scalebar scale", min_value=0.1, max_value=2.0, value=1.0, step=0.05
            )
        with st.expander("Colors", expanded=False):
            col, ref, shading = st.columns(3)
            with col:
                main_color = st.color_picker(
                    "Curve color",
                    value="#2ca50b",
                    key="main_color",
                    # on_change=update_color,
                )
            with ref:
                ref_color = st.color_picker(
                    "Reference color",
                    value="#0886b9",
                    key="ref_color",
                    # on_change=update_ref,
                )
            with shading:
                shade_color = st.color_picker(
                    "Shading color",
                    value="#cccccc",
                    key="shade_color",
                    # on_change=update_shade,
                )
    if eje_x == "t":
        norm_lims_default = [0.21, 0.245]
    else:
        norm_lims_default = [340.0, 410.0]
    #   Everything in a try to avoid errors from no files in first run
    # is not None:
    try:
        # Extract file contents and names
        file_hashes = []
        file_contents = []
        file_names = []
        for uploaded_file in files:
            file_hash, file_content = ld.compute_file_hash(uploaded_file)
            file_hashes.append(file_hash)
            file_contents.append(file_content)  # Store file content
            file_names.append(uploaded_file.name)  # Store file name separately
        #   Scan file names for relevant info and load them as dictionary with tuples dataframes.
        #   The first dataframe (big_data[Ta][0])
        #   contains data for Ta measurement and the second element (big_data[Ta][1]) is the reference.
        temps, big_data, chip_name = ld.load_files(
            file_contents, file_names, [load_begin, load_fin], eje_x
        )
        # common_substring = common_substrings(file_names)
        # # st.write(common_substring)
        # if common_substring != []:
        #     chip_name = common_substring[0]
        # else:
        #     chip_name = 'Unknown_Chip'
        #   Initialize session state for each Ta to store the delta
        #for i in temps:
            # key_name = f'delta_{i}'
            # if key_name not in st.session_state:
            #    st.session_state[key_name] = 0.  # Initial value for each key
            #if f"slider_value_{i}" not in st.session_state:
            #    st.session_state[f"slider_value_{i}"] = 0.0
        if "selected_key" not in st.session_state:
            st.session_state.selected_key = temps[0]
        #   Initialize list to store integral results
        ints = []
        #   Create MODIFY mode checkbox
        with ctr_panel:
            mode = st.radio("mode", ["FULL", "MODIFY", "NORMALIZE"], horizontal=True)
        if mode == 'FULL':
            with inte:
                reverse_col, grid_col = st.columns([.7, .3])
                with reverse_col:
                    reverse_temp = st.checkbox('Flip temperatures')
                with grid_col:
                    toggle_grid = st.checkbox('Grid')
                margin_step = (
                    st.slider("margin_step", min_value=0, max_value=100, value=10) / 100
                                )
        for i in temps:
            if f"delta_{i}" in st.session_state:
                #   Apply delta modification to all curves
                big_data[i][0]["Heat Flow"] += (st.session_state[f"delta_{i}"] / 10) * big_data[i][0]["Heat Flow"].max()
        # if mode != 'FULL':
        #     for i in temps:
            if "x_change_check" not in st.session_state:
                st.session_state["x_change_check"] = "easteregg"
            #   Initialize session_state with the auto-generated limits
            regs_label = "regs_" + str(i)
            if regs_label not in st.session_state or st.session_state["x_change_check"] != eje_x:
                #   Find auto-limits for integration
                
                left, right = fai.find_int_region(
                    big_data[i],
                    int_dif_th
                    * (big_data[i][0]["Heat Flow"] - big_data[i][1]["Heat Flow"]).max(),
                    "Heat Flow",
                )
                
                st.session_state["regs_" + str(i)] = [
                    big_data[i][0][eje_x][left],
                    big_data[i][0][eje_x][right],
                ]
                if i == temps[-1]:
                    st.session_state["x_change_check"] = eje_x
            #st.session_state[f"int_limits_{i}"] = st.session_state["regs_" + str(i)]
            #st.session_state["regs_" + str(i)] = st.session_state[f"int_limits_{i}"]
        
        if mode == "MODIFY":
            #   Create selectbox to select curve to modify
            #selected_keys = st.session_state.selected_key  # Retrieve the selected key
            with ctr_panel:
                Ta = selected_key = st.selectbox(
                    "Select Ta to modify", [i for i in temps], key="selected_key"
                )
            for i in temps:
                if f"new_delta_{i}" not in st.session_state:
                    st.session_state[f"new_delta_{i}"] = 0.
                if f"delta_{i}" not in st.session_state:
                    st.session_state[f"delta_{i}"] = 0.
            if f'has_changed_{Ta}' not in st.session_state:
                st.session_state[f'has_changed_{Ta}'] = True
            if st.session_state[f"new_delta_{Ta}"] != 0.:
                st.session_state[f"delta_{Ta}"] = st.session_state[f"new_delta_{Ta}"]
                st.session_state[f'has_changed_{Ta}'] = False
            elif st.session_state[f'has_changed_{Ta}']:
                st.session_state[f"delta_{Ta}"] = st.session_state[f"new_delta_{Ta}"]
            with ctr_panel:
                current_delta = st.slider(
                    f"Set the delta of Ta = {Ta}",
                    min_value=-1.0,
                    max_value=1.0,
                    key=f"new_delta_{Ta}",
                    value=st.session_state[f"delta_{Ta}"],
                    step = .01
                )
                #st.write(st.session_state[f"delta_{Ta}"])
            #   INTEGRATION LOOP
        
            if mode == 'MODIFY':

                if f'new_lims_{Ta}' not in st.session_state:
                    st.session_state[f'new_lims_{Ta}'] = st.session_state["regs_" + str(Ta)]
                st.session_state["regs_" + str(Ta)] = st.session_state[f'new_lims_{Ta}']
                with ctr_panel:
                    slider_limits = st.slider(
                        "Integration limits",
                        min_value=big_data[int(Ta)][0][eje_x].min(),
                        max_value=big_data[int(Ta)][0][eje_x].max(),
                        value=st.session_state["regs_" + str(Ta)],
                        key=f'new_lims_{Ta}',
                        step=(
                            big_data[int(Ta)][0][eje_x].max()
                            - big_data[int(Ta)][0][eje_x].min()
                        )
                        / 500,
                    )            
            with ctr_panel:
                #   Check if you want to show difference plot
                show_dif = st.checkbox("Show dif")
                smooth_dif = st.checkbox("Smooth dif")
                if mode == 'MODIFY':
                    dif = big_data[int(Ta)][0]["Heat Flow"] - big_data[int(Ta)][1]["Heat Flow"]
                #   Difference plot controls in two columns (30% width for scale and 70% for position)
                scale, delta = st.columns([0.3, 0.7])
                if show_dif:
                    with scale:
                        dif_scale = st.text_input("difference scale", value="1")
                    with delta:
                        dif_delta = st.slider(
                            "dif delta",
                            max_value=1.0,
                            min_value=0.0,
                            value=0.9,
                            key="dif_delta_key",
                        )
                if smooth_dif:
                    with scale:
                        smooth_poly = st.number_input("Polynomial order", value=2)
                    with delta:
                        smooth_window = st.slider(
                                "smooth window",
                                max_value=int(len(dif)*.5),
                                min_value=2,
                                value=30,
                                key="smooth_window",
                            )
                    if smooth_dif:
                        dif = savgol_filter(dif, smooth_window, smooth_poly)
                #   Calculate difference between curves
                # st.write(Ta, type(Ta))
                #   Divide into three columns: one for each color to define
                col, ref, shading = st.columns(3)
                #   Create color pickers in each column for each color
            dif_df = pd.DataFrame()
            for i in temps:
                        #   Find indices of integration limit in the DataFrame
                indices = big_data[i][0][eje_x][
                    (big_data[i][0][eje_x] >= st.session_state["regs_" + str(i)][0])
                    & (big_data[i][0][eje_x] <= st.session_state["regs_" + str(i)][1])
                ].index
                start_idx = big_data[i][0].index[0]
                y_dif = (big_data[i][0]["Heat Flow"]
                    - big_data[i][1]["Heat Flow"])
                if smooth_dif:
                    y_dif = savgol_filter(y_dif, smooth_window, smooth_poly)

                else:
                    y_dif = np.array(y_dif)

                y_dif_integrated = y_dif[indices.min()-start_idx: indices.max()-start_idx]
          
                    # nan_indices = y.index[y.isna()].tolist()
                    # y_clean = y.dropna()
                x = np.array(big_data[i][0]["t"])[indices.min()-start_idx: indices.max()-start_idx]
                dif_df[f'x_{i}'] = np.array(big_data[i][0]["t"])
                dif_df[f'dif_{i}'] = y_dif
                #x_clean = x[~y.isna()]
                ints.append([i, np.trapezoid(y_dif_integrated, x)])
                intsdf = pd.DataFrame(ints, columns=["temps", "enthalpies"])
            color_list = [main_color, ref_color]
            fill_type = ["tonexty", None]
            width = [2, 1.5]
            if mode == 'MODIFY':
                csv_buffer = StringIO()
                dif_df.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                with ctr_panel:
                    st.download_button(
                        label="Download dif",
                        data=csv_data,
                        file_name=f'{chip_name}difs.csv',
                        mime='text/csv'
                    )
                x_max = st.session_state["regs_" + str(Ta)][1]
                x_min = st.session_state["regs_" + str(Ta)][0]
                for i in [1, 0]:
                    #st.write(i, fill_type[i])
                    fig.add_trace(
                        go.Scatter(
                            x=big_data[int(Ta)][i][eje_x],
                            y=big_data[int(Ta)][i]["Heat Flow"],
                            #line_color=color_list[i],
                            # fill=fill_type[i],
                            # fillcolor=shade_color,
                            mode="lines",
                            line = dict(color = color_list[i], width=width[i]),
                        )
                    )
                    
                    #   Plot integration limits
                    fig.add_vline(
                        x=st.session_state["regs_" + str(Ta)][i],
                        line_dash="dash",
                        line_color="red",
                    )
                for i in [1,0]:
                    integration_mask = (big_data[int(Ta)][i][eje_x] >= x_min) & (big_data[int(Ta)][i][eje_x] <= x_max)

                    fig.add_trace(
                        go.Scatter(
                            x=big_data[int(Ta)][i][eje_x][integration_mask],
                            y=big_data[int(Ta)][i]["Heat Flow"][integration_mask],
                            fill=fill_type[i],
                            fillcolor=shade_color,
                            mode="lines",
                            line=dict(color=color_list[i], width=width[i]),
                        )
                    )
                #   Plot difference
                if show_dif:
                    if len(big_data[int(Ta)][0][eje_x]) == len(dif):
                        fig.add_trace(
                            go.Scatter(
                                x=big_data[int(Ta)][0][eje_x],
                                y=float(dif_scale) * dif
                                + dif_delta * np.abs(big_data[int(Ta)][0]["Heat Flow"].min()),
                                mode="lines",
                            )
                        )
                    else:
                        fig.add_trace(
                            go.Scatter(
                                x=big_data[int(Ta)][1][eje_x],
                                y=float(dif_scale) * dif
                                + dif_delta * np.abs(big_data[int(Ta)][0]["Heat Flow"].min()),
                                mode="lines",
                            )
                        )
            #except ValueError:
            #    st.write(
            #        i,
            #        "Error with int limits",
            #        big_data[i][0]["Heat Flow"][indices.min() : indices.max()]
            #        - big_data[i][1]["Heat Flow"][indices.min() : indices.max()],
            #    )
            #except TypeError:
            #    with ctr_panel:
            #        st.write(i, "Modify integral limits")
        if mode == "MODIFY":
            lower_y = (
                min(ints, key=lambda x: x[1])[1] - 0.5 * max(ints, key=lambda x: x[1])[1]
            )
            upper_y = (
                max(ints, key=lambda x: x[1])[1] + 0.5 * max(ints, key=lambda x: x[1])[1]
            )
            cmap = plt.get_cmap("Blues")
            colors = np.linspace(0.3, 1, len(temps))
            # color = []
            for i in range(len(temps)):
                color = cmap(colors[i])
                ints[i].append(str(rgb2hex(color)))
            intsdf = pd.DataFrame(ints, columns=["temps", "enthalpies", "cols"])
            fig2 = px.scatter(intsdf, x="temps", y="enthalpies")
            fig2.update_traces(marker=dict(color=intsdf["cols"], size=10))
            fig2.update_layout(showlegend=False)
            # ax2.plot(temps[i], ints[i][1], "o", color = color)
            yaxis_range = [
                min(min(big_data[Ta][0]["Heat Flow"]), min(big_data[Ta][1]["Heat Flow"]))
                * 0.98,
                np.abs(max(max(big_data[Ta][0]["Heat Flow"]), max(big_data[Ta][1]["Heat Flow"])))
                * 1.01,
            ]
        if mode == "NORMALIZE":
            #   Set plotting limits
            lower_y, upper_y = -0.1, 0.4
            yaxis_range = [
                min(
                    min(big_data[temps[-1]][0]["Heat Flow"]),
                    min(big_data[temps[-1]][1]["Heat Flow"]),
                )
                * 0.98,
                max(
                    max(big_data[temps[-1]][0]["Heat Flow"]),
                    max(big_data[temps[-1]][1]["Heat Flow"]),
                )
                * 1.01,
            ]
            with ctr_panel:
                norm_lims = st.slider(
                    "norm limits",
                    min_value=big_data[temps[-1]][1][eje_x].min(),
                    max_value=big_data[temps[-1]][1][eje_x].max(),
                    value=norm_lims_default,
                    key="norm_lims_key",
                    step=(
                        big_data[temps[-1]][1][eje_x].max()
                        - big_data[temps[-1]][1][eje_x].min()
                    )
                    / 100.0,
                    format = '%.4f'
                )
            fig.add_trace(
                go.Scatter(
                    x=big_data[temps[-1]][1][eje_x],
                    y=big_data[temps[-1]][1]["Heat Flow"],
                    mode="lines",
                )
            )
            for i in [0, 1]:
                fig.add_vline(x=norm_lims[i], line_color="blue", line_dash="dash")
            filtered_series = big_data[temps[-1]][1][eje_x][
                (big_data[temps[-1]][1][eje_x] >= norm_lims[0]) &
                (big_data[temps[-1]][1][eje_x] <= norm_lims[1])
            ]
            start_index = big_data[temps[-1]][1][eje_x].index[0]
            norm_indices = filtered_series.index 
            #st.write(big_data[temps[-1]][1][eje_x].index)
            try:
                m = (
                    big_data[temps[-1]][1]["Heat Flow"][norm_indices.max()]
                    - big_data[temps[-1]][1]["Heat Flow"][norm_indices.min()]
                ) / (
                    (
                        big_data[temps[-1]][1][eje_x][norm_indices.max()]
                        - big_data[temps[-1]][1][eje_x][norm_indices.min()]
                    )
                )
                b = (
                    big_data[temps[-1]][1]["Heat Flow"][norm_indices.min()]
                    - m * big_data[temps[-1]][1][eje_x][norm_indices.min()]
                )
                norm_ref = (
                    b
                    + m
                    * big_data[temps[-1]][1]["t"][norm_indices.min() - start_index: norm_indices.max() - start_index]
                )
                norm_value = np.trapezoid(
                    big_data[temps[-1]][1]["Heat Flow"][
                        norm_indices.min() - start_index : norm_indices.max() - start_index
                    ]
                    - norm_ref,
                    big_data[temps[-1]][0]["t"][norm_indices.min() - start_index : norm_indices.max() - start_index],
                )
                if eje_x == 't':
                    fig.add_trace(
                        go.Scatter(
                            x=big_data[temps[-1]][1]["t"][norm_indices.min() - start_index : norm_indices.max() - start_index],
                            y=norm_ref,
                            mode="lines",
                            )
                        )
                cmap = plt.get_cmap("Blues")
                colors = np.linspace(0.3, 1, len(temps))
                for i in range(len(temps)):
                    color = cmap(colors[i])
                    ints[i].append(str(rgb2hex(color)))
                intsdf = pd.DataFrame(ints, columns=["temps", "enthalpies", "cols"])
                intsdf["enthalpies"] = intsdf["enthalpies"] / norm_value
                fig2 = px.scatter(intsdf, x="temps", y="enthalpies")
                fig2.update_traces(marker=dict(color=intsdf["cols"]))
                fig2.update_layout(showlegend=False)
                fig2.update_layout(yaxis_range=[-0.1, 0.4])
            except KeyError:
                st.write("set Tm limits")
        if mode == "FULL":
            #   Code for MAIN plot with all the curves
            #   Define the margin using the previously defined margin_step by multiplying the step times
            #   the difference between max and min of first curve
            # st.write(big_data[temps[0]][1])
            margin = margin_step * (
                float(big_data[temps[0]][1]["Heat Flow"].max())
                - float(big_data[temps[0]][1]["Heat Flow"].min())
            )
            #   move down relative to the previous curve, so the loop starts with the second curve and moves
            for i in range(1, len(big_data)):
                #   Calculate the difference between consecutive Ta curves - the minimum separation required
                dif = max(abs(
                    big_data[temps[i]][0]["Heat Flow"]
                    - big_data[temps[i - 1]][0]["Heat Flow"]
                ).max(),
                abs(
                    big_data[temps[i]][1]["Heat Flow"]
                    - big_data[temps[i - 1]][1]["Heat Flow"]
                ).max(),
                abs(
                    big_data[temps[i]][0]["Heat Flow"]
                    - big_data[temps[i - 1]][1]["Heat Flow"]
                ).max(),
                abs(
                    big_data[temps[i]][1]["Heat Flow"]
                    - big_data[temps[i - 1]][0]["Heat Flow"]
                ).max(),)
                if not reverse_temp:
                    #   Move both main and reference curves down by
                    big_data[temps[i]][0]["Heat Flow"] -= dif + margin
                    big_data[temps[i]][1]["Heat Flow"] -= dif + margin
                else:
                    #   Shift curve up
                    big_data[temps[i]][0]["Heat Flow"] += dif + margin
                    big_data[temps[i]][1]["Heat Flow"] += dif + margin
            yaxis_range = [
                min(
                    min(big_data[temps[-1]][0]["Heat Flow"]),
                    min(big_data[temps[-1]][1]["Heat Flow"]),
                )
                * 0.98,
                max(
                    max(big_data[temps[0]][0]["Heat Flow"]),
                    max(big_data[temps[0]][1]["Heat Flow"]),
                )
                * 1.01,
            ] if not reverse_temp else [
                min(
                    min(big_data[temps[0]][0]["Heat Flow"]),
                    min(big_data[temps[0]][1]["Heat Flow"]),
                )
                * 0.98,
                max(
                    max(big_data[temps[-1]][0]["Heat Flow"]),
                    max(big_data[temps[-1]][1]["Heat Flow"]),
                )
                * 1.01,]

            with ctr_panel:
                # Define all possible column keys
                column_keys = ['Index', 't', 'Tr', 'Ts', 'Heat Flow']

                selected_columns = st.multiselect(
                    "Select columns to keep:",
                    options=column_keys,
                    default=['Tr', 'Heat Flow']  # all selected by default
                                    )
                # Filter columns whose name contains any of the selected keys
                data_csv_string = bigdata_to_csv(big_data, selected_cols=selected_columns)
                
                st.download_button(
                        label="Download CSV",
                        data=data_csv_string,
                        file_name=f"{chip_name}data.csv",       #   Chip names in downloads
                        mime="text/csv"
                                    )
            #st.dataframe(big_data)
            for i in temps:
                color_list = [main_color, ref_color]
                fill_type = ["tonexty", None]
                text = ["", i]
                width = [2, 1.5]
                x_max = st.session_state["regs_" + str(i)][1]
                x_min = st.session_state["regs_" + str(i)][0]
                
                for j in [1, 0]:
                    fig.add_trace(
                        go.Scatter(
                            x = big_data[i][j][eje_x],
                            y=big_data[i][j]["Heat Flow"],
                            #line_color=color_list[j],
                            # fill=fill_type[j],
                            # fillcolor=shade_color,
                            line = dict(color=color_list[j], width = width[j])
                        )
                    )
                    fig.add_annotation(
                        x=big_data[i][j][eje_x].iloc[-1]
                        * 1.05,  # x position of the last point
                        y=big_data[i][j]["Heat Flow"].iloc[
                            -1
                        ],  # y position of the last point
                        text=text[j],  # The text you want to display
                        showarrow=False,  # Optionally show an arrow pointing to the last point
                        arrowhead=2,  # Customize the arrowhead
                        ax=20,
                        ay=-20,  # Adjust the position of the annotation
                        font=dict(
                            size=15, color="black"
                        ),  # Customize the appearance of the text
                    )
                for j in [1, 0]:
                    integration_mask = (big_data[int(i)][j][eje_x] >= x_min) & (big_data[int(i)][j][eje_x] <= x_max)
                    fig.add_trace(
                        go.Scatter(
                            x = big_data[i][j][eje_x][integration_mask],
                            y=big_data[i][j]["Heat Flow"][integration_mask],
                            #line_color=color_list[j],
                            fill=fill_type[j],
                            fillcolor=shade_color,
                            line = dict(color=color_list[j], width = width[j])
                        )
                    )
                #   Plot the labels on each curve
                fig.update_traces(textposition="middle right")
                fig.update_xaxes(
                                showline=True,
                                ticks='outside',
                                tickcolor='black',
                                minor=dict(ticklen=2))
                if toggle_grid:
                    fig.update_xaxes(
                        showgrid=True,
                        gridcolor="#C7C7C7",
                        griddash='dash',
                        minor_griddash='dash',

                    )

        if mode != "FULL":
            with inte:
                fig2.update_traces(marker=dict(color=intsdf["cols"], size=10))
                fig2.update_layout(showlegend=False)
                st.plotly_chart(fig2,  config={'responsive':True})
                _, dwl_ent, _ = st.columns([0.7, 1, 0.7])
                result_string = "\n".join(
                    f"{row['temps']}\t{row['enthalpies']}"
                    for index, row in intsdf.iterrows()
                )
                ent_filename = f'{chip_name}enthalpies_normalized.csv' if mode == 'NORMALIZE' else f'{chip_name}enthalpies.csv'
                with dwl_ent:
                    st.download_button(label= "download enthalpies",
                                    data = result_string,
                                    file_name=ent_filename,
                                    mime="text/csv")
        #   Show main graph
        xaxis_range = [load_begin * 0.98, load_fin * 1.05]
        sc.add_scalebar(fig, xaxis_range, yaxis_range, scale_factor=scalebar_scale)
        if eje_x != 't':
            fig.update_layout(
                showlegend=False,
                height=700,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(visible=True),
                yaxis=dict(visible=False),
                xaxis_title='Temperature / ºC',
            )
        else:
                    fig.update_layout(
                showlegend=False,
                height=700,
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(visible=True),
                yaxis=dict(visible=False),
                xaxis_title='Time / s',
            )
        with graf:
            st.plotly_chart(fig, config={'responsive':True})#width = 'container', **{"config": config})
    except IndexError:
        with graf:
            st.markdown('<p class="big-font">Upload Files</p>', unsafe_allow_html=True)
    
    except UnboundLocalError:
        pass
    except Exception as e:
        st.write(e)
    #except TypeError:
    #    with graf:
    #        st.markdown('<p class="big-font">Missing File:</p>', unsafe_allow_html=True)
    #        for key, (df1, df2) in big_data.items():
    #            if df1 is None:
    #                st.write("Ta = ", key)
    #            if df2 is None:
    #                st.write("Ta = ", key, "_ref")
    #except KeyError:
    #    with graf:
    #        st.markdown('<p class="big-font">Upload Files</p>', unsafe_allow_html=True)
