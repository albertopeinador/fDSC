import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import filehandler as tx
import file_loader as ld
import find_and_int as fai
import numpy as np

# import scipy.integrate as sc


#   Set layout to wide screen
st.set_page_config(layout="wide")


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


#   Initialize session states

if "slider_delta" not in st.session_state:
    st.session_state["slider_delta"] = 0.0

if "dif_delta" not in st.session_state:
    st.session_state["dif_delta"] = 0.0



#   Define slider updaters for the session_state sliders


def update_slider_value():
    st.session_state[Ta] = st.session_state["slider_delta"]


def update_slider_value_left():
    st.session_state["regs_" + str(Ta)][0] = st.session_state["slider_left"]


def update_slider_value_right():
    st.session_state["regs_" + str(Ta)][1] = st.session_state["slider_right"]


def update_color():
    st.session_state["color"] = st.session_state["main_color"]


def update_ref():
    st.session_state["ref"] = st.session_state["ref_color"]


def update_shade():
    st.session_state["shade"] = st.session_state["shade_color"]


def update_dif_delta():
    st.session_state["dif_delta"] = st.session_state["dif_delta_key"]


#   Initialize session_state colors

if "color" not in st.session_state:
    st.session_state["color"] = "#2ca50b"
if "ref" not in st.session_state:
    st.session_state["ref"] = "#0886b9"
if "shade" not in st.session_state:
    st.session_state["shade"] = "#cccccc"


#   Define figures and axis for the plots

fig, ax1 = plt.subplots(1, 1, sharex=False, sharey=True)
fig.set_figheight(9)
fig2, ax2 = plt.subplots(1, 1, sharex=False, sharey=True)
fig2.set_figheight(5)


#   Create the three main columns - one for main controls (20% of the screen), one for the plots (40%)
#       and one last one for the integrals plot and some adicional controls

ctr_panel, graf, inte = st.columns([0.2, 0.4, 0.4])

#   Set some of the controls from the first column. load_cutoff is position of first data point to load,
#       margin_step is a percent of separation between curves, int_dif_th is threshold for integration,
#       rest are self-explanatory

with ctr_panel:
    folder_name = st.text_input("Folder name", key="direc")
    load_cutoff = st.slider("cutoff", min_value=2, max_value=100, value=75)
    margin_step = st.slider("margin_step", min_value=0, max_value=100, value=10) / 100
    eje_x = st.selectbox("x axis", ["Tr", "Ts", "t"])
    int_dif_th = 0.0
    # int_dif_th = st.slider("integral threshold", min_value=0, max_value=100) / 1000

#   Everything in a try to avoid errors from no files in first run

try:
    #   Scan and find files
    temps, file_dict = tx.files_to_dict(folder_name)

    #   Initialize session state for each Ta to store the delta
    for i in temps:
        if i not in st.session_state:
            st.session_state[i] = 0.0

    #   Load the found files into list of tuples of pd.DataFrames. In each tuple the first df [0] is the
    #       main curve, the second [1], is the reference curve. This will also create a '_modified.txt'
    #       formated for pandas reading.
    big_data = ld.load_files(folder_name, temps, file_dict, load_cutoff)

    #   Initialize some dictionaries and list to store integral limits and results
    int_regs = {}
    ints = []
    lims = {}

    #   Create MODIFY mode checkbox
    with ctr_panel:
        mod = st.checkbox("MODIFY")

    if mod:
        #   Clear the axis in case they contain anything from previous runs
        plt.cla()

        #   Add modification controls to first column
        with ctr_panel:
            #   Define curve to modify from its Ta
            Ta = st.selectbox("Ta", temps)

            #   Define delta for the selected curve, this will be added to the main curve
            st.slider(
                "delta",
                min_value=-1.0,
                max_value=1.0,
                value=st.session_state[Ta],
                key="slider_delta",
                step=0.01,
                on_change=update_slider_value,
            )
            
            show_dif = st.checkbox("Show dif")

            scale, delta = st.columns([0.3, 0.7])
            if show_dif:
                with scale:
                    dif_scale = st.text_input("difference scale", value="1")
                with delta:
                    dif_delta = st.slider(
                        "dif delta",
                        max_value=1.0,
                        min_value=0.0,
                        value=st.session_state["dif_delta"],
                        key="dif_delta_key",
                        on_change=update_dif_delta,
                    )

    #   INTEGRATION LOOP
    for i in range(len(temps)):
        #   Apply delta modification to all curves
        big_data[i][0]["Heat Flow"] += (st.session_state[temps[i]] / 10) * big_data[i][
            0
        ]["Heat Flow"].max()

        if 'x_change_check'+str(temps[i]) not in st.session_state:
            st.session_state['x_change_check'+str(temps[i])] = 'easteregg'


        #   Initialize session_state with the auto-generated limits
        regs_label = "regs_" + str(temps[i])
        if regs_label not in st.session_state or st.session_state['x_change_check'+str(temps[i])] != eje_x:
            #   Find auto-limits for integration
            left, right = fai.find_int_region(
                big_data[i],
                int_dif_th
                * (big_data[i][0]["Heat Flow"] - big_data[i][1]["Heat Flow"]).max(),
                "Heat Flow",
            )
            st.session_state[regs_label] = [
                big_data[i][0][eje_x].iloc[left],
                big_data[i][0][eje_x].iloc[right],
            ]
            st.session_state['x_change_check'+str(temps[i])] = eje_x

        #   Find indices of integration limit in the DataFrame
        indices = big_data[i][0][eje_x][
            (big_data[i][0][eje_x] >= st.session_state[regs_label][0])
            & (big_data[i][0][eje_x] <= st.session_state[regs_label][1])
        ].index
        
        #   Try to calculate integral, sometimes it wont work because auto-limits are a bit finicky
        try:
            ints.append(
                np.trapezoid(
                    big_data[i][0]["Heat Flow"][indices.min() : indices.max()]
                    - big_data[i][1]["Heat Flow"][indices.min() : indices.max()],
                    big_data[i][0]["t"][indices.min() : indices.max()],
                )
            )
        except ValueError:
            st.write(temps[i], "Error with int limits")
        except TypeError:
            st.write(temps[i], 'Modify integral limits')

    #   Plot calculated integrals
    try:
        ax2.plot(temps, ints, "ks")
    except ValueError:
        #print("int not working")
        st.write('')
    #   Add extra MODIFY controls over the integral graph
    with inte:

        # Further divide the space into two columns
        low, up = st.columns(2)

        #   In one column get a text input for the lower plotting limit of integral plot
        with low:
            lower = st.text_input("Lower Ta limit", key="lower", value="-100")

        #   In the other for the upper limit
        with up:
            upper = st.text_input("Upper Ta limit", key="upper", value="300")

    #   Set plotting limits
    ax2.set_xlim((int(lower), int(upper)))

    if mod:

        #   Calculate difference between curves
        dif = (
            big_data[temps.index(Ta)][0]["Heat Flow"]
            - big_data[temps.index(Ta)][1]["Heat Flow"]
        )

        #   Plot curves being modified
        big_data[temps.index(Ta)][0].plot(
            x=eje_x,
            y="Heat Flow",
            ax=ax1,
            legend=False,
            style=st.session_state["color"],
        )
        big_data[temps.index(Ta)][1].plot(
            x=eje_x,
            y="Heat Flow",
            ax=ax1,
            legend=False,
            style=st.session_state["ref"],
            linewidth=1.6,
        )

        #   Plot integration limits
        ax1.axvline(x=st.session_state["regs_" + str(Ta)][0], color="r", linestyle="--")
        ax1.axvline(x=st.session_state["regs_" + str(Ta)][1], color="r", linestyle="--")

        #   Plot difference
        if show_dif:
            if len(big_data[temps.index(Ta)][0][eje_x]) == len(dif):
                ax1.plot(
                    big_data[temps.index(Ta)][0][eje_x],
                    float(dif_scale) * dif
                    + dif_delta
                    * np.abs(big_data[temps.index(Ta)][0]["Heat Flow"].min()),
                    "r",
                )  # [lims[Ta][0]:lims[Ta][1]+2]
            else:
                ax1.plot(
                    big_data[temps.index(Ta)][1][eje_x],
                    float(dif_scale) * dif
                    + dif_delta
                    * np.abs(big_data[temps.index(Ta)][0]["Heat Flow"].min()),
                    "r",
                )  # [lims[Ta][0]:lims[Ta][1]+2]

        #   Plot shading
        if len(big_data[temps.index(Ta)][0]["Heat Flow"]) < len(
            big_data[temps.index(Ta)][1]["Heat Flow"]
        ):
            ax1.fill_between(
                big_data[temps.index(Ta)][0][eje_x],
                big_data[temps.index(Ta)][0]["Heat Flow"],
                big_data[temps.index(Ta)][1]["Heat Flow"].iloc[
                    : len(big_data[temps.index(Ta)][0]["Heat Flow"])
                ],
                color=st.session_state["shade"],
            )
        else:
            ax1.fill_between(
                big_data[temps.index(Ta)][1][eje_x],
                big_data[temps.index(Ta)][0]["Heat Flow"].iloc[
                    : len(big_data[temps.index(Ta)][1]["Heat Flow"])
                ],
                big_data[temps.index(Ta)][1]["Heat Flow"],
                color=st.session_state["shade"],
            )

    #   Show integral plot
    with inte:
        st.pyplot(fig2)
        

    if mod:

        #   Create sliders for integration limits
        with inte:
            #   Keep in mind time scale is much smaller and thus require smaller step - this as a whole is annoying
            if eje_x == "t":
                
                st.slider(
                    "left integration limit",
                    min_value=big_data[temps.index(Ta)][0][eje_x].min(),
                    max_value=float(st.session_state["regs_" + str(Ta)][1]),
                    value=float(st.session_state["regs_" + str(Ta)][0]),
                    key="slider_left",
                    on_change=update_slider_value_left,
                    step=0.001,
                )
            else:
                st.slider(
                    "left integration limit",
                    min_value=big_data[temps.index(Ta)][0][eje_x].min(),
                    max_value=float(st.session_state["regs_" + str(Ta)][1]),
                    value=float(st.session_state["regs_" + str(Ta)][0]),
                    key="slider_left",
                    on_change=update_slider_value_left,
                    step=0.1,
                )
            if eje_x == "t":
                st.slider(
                    "right integration limit",
                    min_value=float(st.session_state["regs_" + str(Ta)][0]),
                    max_value=big_data[temps.index(Ta)][0][eje_x].max(),
                    value=float(st.session_state["regs_" + str(Ta)][1]),
                    key="slider_right",
                    on_change=update_slider_value_right,
                    step=0.001,
                )
            else:
                st.slider(
                    "right integration limit",
                    min_value=float(st.session_state["regs_" + str(Ta)][0]),
                    max_value=big_data[temps.index(Ta)][0][eje_x].max(),
                    value=float(st.session_state["regs_" + str(Ta)][1]),
                    key="slider_right",
                    on_change=update_slider_value_right,
                    step=0.1,
                )

            #   Divide into three columns: one for each color to define
            col, ref, shading = st.columns(3)
            #   Create color pickers in each column for each color
            with col:
                st.color_picker(
                    "Curve color",
                    value=st.session_state["color"],
                    key="main_color",
                    on_change=update_color,
                )
            with ref:
                st.color_picker(
                    "Reference color",
                    value=st.session_state["ref"],
                    key="ref_color",
                    on_change=update_ref,
                )
            with shading:
                st.color_picker(
                    "Shading color",
                    value=st.session_state["shade"],
                    key="shade_color",
                    on_change=update_shade,
                )

    else:
        #   Code for MAIN plot with all the curves

        #   Define the margin using the previously defined margin_step
        margin = margin_step * (
            float(big_data[0][1]["Heat Flow"].max())
            - float(big_data[0][1]["Heat Flow"].min())
        )
        for i in range(1, len(big_data)):

            #   Calculate the difference between consecutive Ta curves - the minimum separation required
            dif = abs(big_data[i][0]["Heat Flow"] - big_data[i - 1][0]["Heat Flow"]).max()

            #   Move both main and reference curves down by
            big_data[i][0]["Heat Flow"] -= dif + margin
            big_data[i][1]["Heat Flow"] -= dif + margin

        for i in range(len(temps)):
            #   Plot the curves
            big_data[i][0].plot(
                x=eje_x,
                y="Heat Flow",
                ax=ax1,
                legend=False,
                style=st.session_state["color"],
            )
            big_data[i][1].plot(
                x=eje_x,
                y="Heat Flow",
                ax=ax1,
                legend=False,
                style=st.session_state["ref"],
                linewidth=1.6,
            )

            #   Plot the labels on each curve
            ax1.text(
                big_data[i][0][eje_x].iloc[-1],
                big_data[i][0]["Heat Flow"].iloc[-1],
                temps[i],
            )

            # Plot the shading
            if len(big_data[i][0]["Heat Flow"]) < len(big_data[i][1]["Heat Flow"]):
                ax1.fill_between(
                    big_data[i][0][eje_x],
                    big_data[i][0]["Heat Flow"],
                    big_data[i][1]["Heat Flow"].iloc[
                        : len(big_data[i][0]["Heat Flow"])
                    ],
                    color=st.session_state["shade"],
                )
            else:
                ax1.fill_between(
                    big_data[i][1][eje_x],
                    big_data[i][0]["Heat Flow"].iloc[
                        : len(big_data[i][1]["Heat Flow"])
                    ],
                    big_data[i][1]["Heat Flow"],
                    color=st.session_state["shade"],
                )

    #   Clear up the graph, remove borders and y axis
    ax1.spines["top"].set_visible(False)
    ax1.spines["left"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.yaxis.set_ticks([])
    ax1.tick_params(axis="y", which="both", length=0)

    #   Show main graph
    with graf:
        st.pyplot(fig)


except FileNotFoundError:
    with graf:
        # st.title('Enter folder name')
        st.markdown('<p class="big-font">Enter Folder Name</p>', unsafe_allow_html=True)
# st.line_chart(data, x = 'Tr', y = 'Heat Flow')
