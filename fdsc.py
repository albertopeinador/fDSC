#import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
#import new_filehandler as fh
import new_file_loader as ld
import find_and_int as fai
import numpy as np
import scalebar as sc
import io

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

'''st.markdown(
    """
    <style>
    /* Target the file uploader to reduce its size */
    .stFileUpload {
        font-size: 12px;
        padding: 5px;
        width: 60%;
    }

    /* Optional: Adjust the file uploader button appearance */
    .stFileUpload label {
        padding: 2px 1px;
        background-color: #f0f0f5;
        border-radius: 4px;
        font-size: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
'''

#   Initialize session states


if "dif_delta" not in st.session_state:
    st.session_state["dif_delta"] = .9
if "color" not in st.session_state:
    st.session_state["color"] = "#2ca50b"
if "ref" not in st.session_state:
    st.session_state["ref"] = "#0886b9"
if "shade" not in st.session_state:
    st.session_state["shade"] = "#cccccc"



#   Define slider updaters for the session_state sliders


def update_slider_value():
    st.session_state[Ta] = st.session_state["slider_delta"]


def update_limits_slider():
    st.session_state["regs_" + str(Ta)] = st.session_state["limits_slider"]


def update_color():
    st.session_state["color"] = st.session_state["main_color"]


def update_ref():
    st.session_state["ref"] = st.session_state["ref_color"]


def update_shade():
    st.session_state["shade"] = st.session_state["shade_color"]


def update_dif_delta():
    st.session_state["dif_delta"] = st.session_state["dif_delta_key"]



#   Define figures and axis for the plots

fig, ax1 = plt.subplots(1, 1, sharex=False, sharey=True, figsize = (2.5*1.968504, 4.44*1.968504), dpi = 300)

fig2, ax2 = plt.subplots(1, 1, sharex=False, sharey=True, figsize = (2.5*1.968504, 2.5*1.968504), dpi = 300)


#   Create the three main columns - one for main controls (20% of the screen), one for the plots (40%)
#       and one last one for the integrals plot and some adicional controls

ctr_panel, graf, inte = st.columns([3, 4, 4])

#   Set some of the controls from the first column. load_cutoff is position of first data point to load,
#       margin_step is a percent of separation between curves, int_dif_th is threshold for integration,
#       rest are self-explanatory

with ctr_panel:
    with st.expander('Load controls', expanded = True):
        files =st.file_uploader('Upload files', accept_multiple_files = True, type = ['txt'], label_visibility='collapsed')
        load_cutoff = st.slider("cutoff", min_value=2, max_value=100, value=75)
        margin_step = st.slider("margin_step", min_value=0, max_value=100, value=10) / 100
        eje_x = st.selectbox("x axis", ["Tr", "Ts", "t"])
        int_dif_th = 0.0
        scalebar_scale = st.slider('scalebar scale', min_value = 0.1, max_value = 2., value = 1., step = .05)


#   Everything in a try to avoid errors from no files in first run

try:
    #   Scan and find files
    temps, big_data = ld.load_files(files, load_cutoff)

    #   Initialize session state for each Ta to store the delta
    for i in temps:
        if i not in st.session_state:
            st.session_state[i] = 0.0

    #   Load the found files into list of tuples of pd.DataFrames. In each tuple the first df [0] is the
    #       main curve, the second [1], is the reference curve. This will also create a '_modified.txt'
    #       formated for pandas reading.

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
    for i in temps:
        
        #   Apply delta modification to all curves
        big_data[i][0]["Heat Flow"] += (st.session_state[i] / 10) * big_data[i][
            0
        ]["Heat Flow"].max()

        if 'x_change_check'+str(i) not in st.session_state:
            st.session_state['x_change_check'+str(i)] = 'easteregg'


        #   Initialize session_state with the auto-generated limits
        regs_label = "regs_" + str(i)
        if regs_label not in st.session_state or st.session_state['x_change_check'+str(i)] != eje_x:
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
            st.session_state['x_change_check'+str(i)] = eje_x

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
            st.write(i, "Error with int limits")
        except TypeError:
            st.write(i, 'Modify integral limits')

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
        mins = .9*np.array(ints).min()
        #   In one column get a text input for the lower plotting limit of integral plot
        with low:
            lower = st.text_input("Lower Ta limit", key="lower", value="-100")
            try:
                lower_y = st.text_input("Lower H limit", key="lower_y", value = str(mins))
            except ValueError:
                st.write('mierda')
        #   In the other for the upper limit
        with up:
            upper = st.text_input("Upper Ta limit", key="upper", value="300")
            upper_y = st.text_input("Upper H limit", key="upper_y", value=str(1.1*max(ints)))
            st.write(ints)
    #   Set plotting limits
    ax2.set_xlim((int(lower), int(upper)))
    ax2.set_ylim((float(lower_y), float(upper_y)))

    if mod:

        #   Calculate difference between curves
        dif = (
            big_data[Ta][0]["Heat Flow"]
            - big_data[Ta][1]["Heat Flow"]
        )

        #   Plot curves being modified
        big_data[Ta][0].plot(
            x=eje_x,
            y="Heat Flow",
            ax=ax1,
            legend=False,
            style=st.session_state["color"],
            linewidth = 1,
        )
        big_data[Ta][1].plot(
            x=eje_x,
            y="Heat Flow",
            ax=ax1,
            legend=False,
            style=st.session_state["ref"],
            linewidth=1.1,
        )

        #   Plot integration limits
        ax1.axvline(x=st.session_state["regs_" + str(Ta)][0], color="r", linestyle="--")
        ax1.axvline(x=st.session_state["regs_" + str(Ta)][1], color="r", linestyle="--")

        #   Plot difference
        if show_dif:
            if len(big_data[Ta][0][eje_x]) == len(dif):
                ax1.plot(
                    big_data[Ta][0][eje_x],
                    float(dif_scale) * dif
                    + dif_delta
                    * np.abs(big_data[Ta][0]["Heat Flow"].min()),
                    "r",
                )  # [lims[Ta][0]:lims[Ta][1]+2]
            else:
                ax1.plot(
                    big_data[Ta][1][eje_x],
                    float(dif_scale) * dif
                    + dif_delta
                    * np.abs(big_data[Ta][0]["Heat Flow"].min()),
                    "r",
                )  # [lims[Ta][0]:lims[Ta][1]+2]

        #   Plot shading
        if len(big_data[Ta][0]["Heat Flow"]) < len(
            big_data[Ta][1]["Heat Flow"]
        ):
            ax1.fill_between(
                big_data[Ta][0][eje_x],
                big_data[Ta][0]["Heat Flow"],
                big_data[Ta][1]["Heat Flow"].iloc[
                    : len(big_data[Ta][0]["Heat Flow"])
                ],
                color=st.session_state["shade"],
            )
        else:
            ax1.fill_between(
                big_data[Ta][1][eje_x],
                big_data[Ta][0]["Heat Flow"].iloc[
                    : len(big_data[Ta][1]["Heat Flow"])
                ],
                big_data[Ta][1]["Heat Flow"],
                color=st.session_state["shade"],
            )

    #   Show integral plot
    
    buffer = io.BytesIO()
    fig2.savefig(buffer, format='pdf')
    buffer.seek(0)
    with inte:
        st.pyplot(fig2, use_container_width=True)
        name, button = st.columns(2)
        with name:
            inte_name = st.text_input('Save as:', label_visibility='collapsed', placeholder='Integral plot name')
        with button:
            st.download_button(
                    label="Download Integral Plot",
                    data=buffer,
                    file_name=inte_name + '.pdf',
                    mime="image/pdf"
                    )        

    if mod:

        #   Create sliders for integration limits
        with inte:
            #   Keep in mind time scale is much smaller and thus require smaller step - this as a whole is annoying
            st.slider(
                "Integration limits",
                min_value=big_data[Ta][0][eje_x].min(),
                max_value=big_data[Ta][0][eje_x].max(),
                value=st.session_state["regs_" + str(Ta)],
                key="limits_slider",
                on_change=update_limits_slider,
                step=(big_data[Ta][0][eje_x].max() - big_data[Ta][0][eje_x].min()) / 500,
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
            float(big_data[temps[0]][1]["Heat Flow"].max())
            - float(big_data[temps[0]][1]["Heat Flow"].min())
        )
        for i in range(1, len(big_data)):

            #   Calculate the difference between consecutive Ta curves - the minimum separation required
            dif = abs(big_data[temps[i]][0]["Heat Flow"] - big_data[temps[i - 1]][0]["Heat Flow"]).max()

            #   Move both main and reference curves down by
            big_data[temps[i]][0]["Heat Flow"] -= dif + margin
            big_data[temps[i]][1]["Heat Flow"] -= dif + margin

        for i in temps:
            #   Plot the curves
            big_data[i][0].plot(
                x=eje_x,
                y="Heat Flow",
                ax=ax1,
                legend=False,
                style=st.session_state["color"],
                linewidth = 1,
            )
            big_data[i][1].plot(
                x=eje_x,
                y="Heat Flow",
                ax=ax1,
                legend=False,
                style=st.session_state["ref"],
                linewidth=1.1,
            )

            #   Plot the labels on each curve
            ax1.text(
                big_data[i][0][eje_x].iloc[-1] *1.01,
                big_data[i][0]["Heat Flow"].iloc[-1],
                i,
                fontsize = 13,
                fontweight = 'book'
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

    scalebar = sc.add_scalebar(scalebar_scale, ax1, matchx = False, hidex = False, )
    buffer1 = io.BytesIO()
    fig.savefig(buffer1, format='pdf')
    buffer1.seek(0)  # Move the cursor to the start of the buffer

    #   Show main graph
    with graf:
        st.pyplot(fig, use_container_width=True)
        name, button = st.columns(2)
        with name:
            plot_name = st.text_input('Save plot as:', label_visibility='collapsed',  placeholder='Plot name')
        with button:
            st.download_button(
                    label="Download Plot",
                    data=buffer1,
                    file_name=plot_name + '.pdf',
                    mime="image/pdf"
                    )        


except IndexError:
    with graf:
        st.markdown('<p class="big-font">Upload Files</p>', unsafe_allow_html=True)
except TypeError:
    with graf:
        st.markdown('<p class="big-font">Missing File:</p>', unsafe_allow_html=True)
        for key, (df1, df2) in big_data.items():
            if df1 is None:
                st.write('Ta = ', key)
            if df2 is None:
                st.write('Ta = ', key, '_ref')