import streamlit as st
import matplotlib.pyplot as plt
import new_file_loader as ld
import find_and_int as fai
import numpy as np
import new_scalebar as sc
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from matplotlib.colors import rgb2hex




#  Set layout to wide screen
#st.set_page_config(layout="wide")

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
            margin_step = (
                st.slider("margin_step", min_value=0, max_value=100, value=10) / 100
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

        #   Scan file names for relevant info and load them as dictionary with tuples dataframes. The first dataframe (big_data[Ta][0])
        #   contains data for Ta measurement and the second element (big_data[Ta][1]) is the reference.

        temps, big_data = ld.load_files(
            file_contents, file_names, [load_begin, load_fin], eje_x
        )

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

        if mode != 'FULL':
            #   INTEGRATION LOOP
            for i in temps:

                #   Apply delta modification to all curves
                big_data[i][0]["Heat Flow"] += (st.session_state[f"delta_{i}"] / 10) * big_data[
                    i
                ][0]["Heat Flow"].max()

                if "x_change_check" not in st.session_state:
                    st.session_state["x_change_check"] = "easteregg"
                #   Initialize session_state with the auto-generated limits
                regs_label = "regs_" + str(i)
                if (regs_label not in st.session_state or st.session_state["x_change_check"] != eje_x):
                    #   Find auto-limits for integration
                    left, right = fai.find_int_region(
                        big_data[i],
                        int_dif_th
                        * (big_data[i][0]["Heat Flow"] - big_data[i][1]["Heat Flow"]).max(),
                        "Heat Flow",
                    )
                    st.session_state["regs_" + str(i)] = [
                        big_data[i][0][eje_x].iloc[left],
                        big_data[i][0][eje_x].iloc[right],
                    ]
                    if i == temps[-1]:
                        st.session_state["x_change_check"] = eje_x
                #st.session_state[f"int_limits_{i}"] = st.session_state["regs_" + str(i)]
                #st.session_state["regs_" + str(i)] = st.session_state[f"int_limits_{i}"]
            with ctr_panel:

                #   Check if you want to show difference plot
                show_dif = st.checkbox("Show dif")
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
                #   Calculate difference between curves
                # st.write(Ta, type(Ta))
                dif = big_data[int(Ta)][0]["Heat Flow"] - big_data[int(Ta)][1]["Heat Flow"]


                #   Divide into three columns: one for each color to define
                col, ref, shading = st.columns(3)
                #   Create color pickers in each column for each color
            
            
            
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
            
            for i in temps:
                        #   Find indices of integration limit in the DataFrame
                indices = big_data[i][0][eje_x][
                    (big_data[i][0][eje_x] >= st.session_state["regs_" + str(i)][0])
                    & (big_data[i][0][eje_x] <= st.session_state["regs_" + str(i)][1])
                ].index
                start_idx = big_data[i][0].index[0]
                y = (big_data[i][0]["Heat Flow"]
                    - big_data[i][1]["Heat Flow"]).iloc[indices.min()-start_idx: indices.max()-start_idx]

                x = big_data[i][0]["t"].iloc[indices.min()-start_idx: indices.max()-start_idx]
                nan_indices = y.index[y.isna()].tolist()
                y_clean = y.dropna()
                x_clean = x[~y.isna()]

                ints.append([i, np.trapz(y_clean, x_clean)])
                intsdf = pd.DataFrame(ints, columns=["temps", "enthalpies"])

            color_list = [main_color, ref_color]
            fill_type = [None, "tonexty"]
            for i in [0, 1]:
                fig.add_trace(
                    go.Scatter(
                        x=big_data[int(Ta)][i][eje_x],
                        y=big_data[int(Ta)][i]["Heat Flow"],
                        line_color=color_list[i],
                        fill=fill_type[i],
                        fillcolor=shade_color,
                        mode="lines",
                    )
                )

                #   Plot integration limits
                fig.add_vline(
                    x=st.session_state["regs_" + str(Ta)][i],
                    line_dash="dash",
                    line_color="red",
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
                max(max(big_data[Ta][0]["Heat Flow"]), max(big_data[Ta][1]["Heat Flow"]))
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
            margin = margin_step * (
                float(big_data[temps[0]][1]["Heat Flow"].max())
                - float(big_data[temps[0]][1]["Heat Flow"].min())
            )
            #   move down relative to the previous curve, so the loop starts with the second curve and moves
            for i in range(1, len(big_data)):

                #   Calculate the difference between consecutive Ta curves - the minimum separation required
                dif = abs(
                    big_data[temps[i]][0]["Heat Flow"]
                    - big_data[temps[i - 1]][0]["Heat Flow"]
                ).max()

                #   Move both main and reference curves down by
                big_data[temps[i]][0]["Heat Flow"] -= dif + margin
                big_data[temps[i]][1]["Heat Flow"] -= dif + margin
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
            ]
            for i in temps:
                color_list = [main_color, ref_color]
                fill_type = [None, "tonexty"]
                text = ["", i]
                for j in [0, 1]:
                    fig.add_trace(
                        go.Scatter(
                            x = big_data[i][j][eje_x],
                            y=big_data[i][j]["Heat Flow"],
                            line_color=color_list[j],
                            fill=fill_type[j],
                            fillcolor=shade_color,
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
                #   Plot the labels on each curve
                fig.update_traces(textposition="middle right")

        if mode != "FULL":

            with inte:
                fig2.update_traces(marker=dict(color=intsdf["cols"], size=10))
                fig2.update_layout(showlegend=False)
                st.plotly_chart(fig2, **{"config": config})
                _, dwl_ent, _ = st.columns([0.7, 1, 0.7])

                result_string = "\n".join(
                    f"{row['temps']}\t{row['enthalpies']}"
                    for index, row in intsdf.iterrows()
                )
                with dwl_ent:
                    st.download_button("download enthalpies", result_string)
        #   Show main graph
        
        xaxis_range = [load_begin * 0.98, load_fin * 1.05]
        sc.add_scalebar(fig, xaxis_range, yaxis_range, scale_factor=scalebar_scale)
        fig.update_layout(
            showlegend=False,
            height=700,
            width = 200,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis=dict(visible=True),
            yaxis=dict(visible=False),
            xaxis_title=eje_x,
        )
        with graf:
            st.plotly_chart(fig, **{"config": config})
    except IndexError:
        with graf:
            st.markdown('<p class="big-font">Upload Files</p>', unsafe_allow_html=True)
    except TypeError:
        with graf:
            st.markdown('<p class="big-font">Missing File:</p>', unsafe_allow_html=True)
            for key, (df1, df2) in big_data.items():
                if df1 is None:
                    st.write("Ta = ", key)
                if df2 is None:
                    st.write("Ta = ", key, "_ref")
    #except KeyError:
    #    with graf:
    #        st.markdown('<p class="big-font">Upload Files</p>', unsafe_allow_html=True)
