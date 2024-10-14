import streamlit as st
import matplotlib.pyplot as plt
import new_file_loader as ld
import find_and_int as fai
import numpy as np
import scalebar as sc
import io

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

fig_dpi = 100




#
#

##   Define slider updaters for the session_state sliders#

  
def update_slider_value():
    if st.session_state[Ta] != st.session_state["delta"]:
        st.session_state[Ta] = st.session_state["delta"]
    st.session_state.pop('delta', None)


def update_limits_slider():
    if st.session_state["regs_" + str(Ta)] != st.session_state["int_limits"]:
        st.session_state["regs_" + str(Ta)] = st.session_state["int_limits"]
    st.session_state.pop('int_limits', None)



#   Define figures and axis for the plots

fig, ax1 = plt.subplots(1, 1, sharex=False, sharey=True, figsize = (2.5*1.968504, 16 / 9 * 2.5*1.968504), dpi = fig_dpi)

fig2, ax2 = plt.subplots(1, 1, sharex=False, sharey=True, figsize = (2.5*1.968504, 2.5*1.968504), dpi = fig_dpi)


#   Create the three main columns - one for main controls, one for the plots
#       and one last one for the integrals plot and some adicional controls

ctr_panel, graf, inte = st.columns([3, 3, 5])
#load_expander = st.expander('Load controls', expanded = True)
#   Set some of the controls from the first column. load_cutoff is position of first data point to load,
#       margin_step is a percent of separation between curves, int_dif_th is threshold for integration,
#       rest are self-explanatory

with ctr_panel:
    with st.expander('Load controls', expanded = True):
        files =st.file_uploader('Upload files', accept_multiple_files = True, type = ['txt'], label_visibility='collapsed')
        eje_x = st.selectbox("x axis", ["Tr", "Ts", "t"])
        load_start, load_end = st.columns (2)
        if eje_x == 't':
            with load_start:
                load_begin = st.number_input("Start at " + eje_x, value=0.005, step = 0.001, format="%.3f")
            with load_end:
                load_fin = st.number_input("End at " + eje_x, value=0.300, step = 0.001, format="%.3f")
        else:
            with load_start:
                load_begin = st.number_input("Start at " + eje_x, value=-80.)
            with load_end:
                load_fin = st.number_input("End at " + eje_x, value=440.)
        margin_step = st.slider("margin_step", min_value=0, max_value=100, value=10) / 100
        int_dif_th = 0.0
        scalebar_scale = st.slider('scalebar scale', min_value = 0.1, max_value = 2., value = 1., step = .05)  
    with st.expander('Colors', expanded = False):
        col, ref, shading = st.columns (3)
        with col:
            main_color = st.color_picker(
                "Curve color",
                value="#2ca50b",
                key="main_color",
                #on_change=update_color,
            )
        with ref:
            ref_color = st.color_picker(
                "Reference color",
                value='#0886b9',
                key="ref_color",
                #on_change=update_ref,
            )
        with shading:
            shade_color = st.color_picker(
                "Shading color",
                value='#cccccc',
                key="shade_color",
                #on_change=update_shade,
            )
if eje_x == 't':
    norm_lims_default = [0.21, .245]
else:
    norm_lims_default = [340., 410.] 
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

    temps, big_data = ld.load_files(file_contents, file_names, [load_begin, load_fin], eje_x)


    #   Initialize session state for each Ta to store the delta
    for temp in temps:
        if temp not in st.session_state:
            st.session_state[temp] = 0.0

    #   Initialize list to store integral results
    ints = []


    #   Create MODIFY mode checkbox
    with ctr_panel:
        mode = st.radio('mode', ['FULL', 'MODIFY', 'NORMALIZE'], horizontal=True)


    
        #   INTEGRATION LOOP
    for i in temps:
        
        #   Apply delta modification to all curves
        big_data[i][0]["Heat Flow"] += (st.session_state[i] / 10) * big_data[i][0]["Heat Flow"].max()
        if 'x_change_check' not in st.session_state:
            st.session_state['x_change_check'] = 'easteregg'
        #   Initialize session_state with the auto-generated limits
        regs_label = "regs_" + str(i)
        if regs_label not in st.session_state or st.session_state['x_change_check'] != eje_x:
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
            if i == temps[-1]:
                st.session_state['x_change_check'] = eje_x
        #   Find indices of integration limit in the DataFrame
        indices = big_data[i][0][eje_x][
            (big_data[i][0][eje_x] >= st.session_state[regs_label][0])
            & (big_data[i][0][eje_x] <= st.session_state[regs_label][1])
        ].index
        
        
        #   Try to calculate integral, sometimes it wont work because auto-limits are a bit finicky
        try:
            ints.append(
                [i, np.trapezoid(
                    big_data[i][0]["Heat Flow"][indices.min() : indices.max()]
                    - big_data[i][1]["Heat Flow"][indices.min() : indices.max()],
                    big_data[i][0]["t"][indices.min() : indices.max()],
                )]
            )
        except ValueError:
            st.write(i, "Error with int limits")
        except TypeError:
            st.write(i, 'Modify integral limits')

    #   Plot calculated integrals

    if mode == 'MODIFY':
        lower_y =  min(ints, key=lambda x: x[1])[1] - .5 * max(ints, key=lambda x: x[1])[1]
        upper_y = max(ints, key=lambda x: x[1])[1] + .5 * max(ints, key=lambda x: x[1])[1]
        #st.write(lower_y, upper_y)
        cmap = plt.get_cmap('Blues')
        colors = np.linspace(0.3, 1, len(temps))
        for i in range(len(temps)):
            color = cmap(colors[i])
            ax2.plot(temps[i], ints[i][1], "o", color = color)
        #   Clear the axis in case they contain anything from previous runs
        #   Add modification controls to first column
        with ctr_panel:
            #   Create selectbox to select curve to modify
            Ta = st.selectbox("Ta", temps)

            #   Define delta for the selected curve, this will be added to the main curve
            slider_delta = st.slider(
                "delta",
                min_value=-1.0,
                max_value=1.0,
                value=st.session_state[Ta],
                key='delta',
                step=0.01,
                on_change=update_slider_value,
            )
            
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
                        value=.9,
                        key="dif_delta_key",
                    )
            #   Calculate difference between curves
            dif = (
                big_data[Ta][0]["Heat Flow"]
                - big_data[Ta][1]["Heat Flow"]
            )
            #   Create sliders for integration limits

            #   Keep in mind time scale is much smaller and thus require smaller step - this as a whole is annoying

            slider_limits = st.slider(
                "Integration limits",
                min_value=big_data[Ta][0][eje_x].min(),
                max_value=big_data[Ta][0][eje_x].max(),
                value=st.session_state['regs_' + str(Ta)],
                key="int_limits",
                on_change=update_limits_slider,
                step=(big_data[Ta][0][eje_x].max() - big_data[Ta][0][eje_x].min()) / 500,)

            #   Divide into three columns: one for each color to define
            col, ref, shading = st.columns(3)
            #   Create color pickers in each column for each color

        #   Plot curves being modified
        big_data[Ta][0].plot(
            x=eje_x,
            y="Heat Flow",
            ax=ax1,
            legend=False,
            style=main_color,
            linewidth = 1,
        )
        big_data[Ta][1].plot(
            x=eje_x,
            y = "Heat Flow",
            ax=ax1,
            legend=False,
            style=ref_color,
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
                )
            else:
                ax1.plot(
                    big_data[Ta][1][eje_x],
                    float(dif_scale) * dif
                    + dif_delta
                    * np.abs(big_data[Ta][0]["Heat Flow"].min()),
                    "r",
                )

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
                color=shade_color,
            )
        else:
            ax1.fill_between(
                big_data[Ta][1][eje_x],
                big_data[Ta][0]["Heat Flow"].iloc[
                    : len(big_data[Ta][1]["Heat Flow"])
                ],
                big_data[Ta][1]["Heat Flow"],
                color=shade_color,
            )

    if mode == 'NORMALIZE':
            #   Set plotting limits
        lower_y, upper_y = -0.1, .4

        with ctr_panel:
            norm_lims = st.slider('norm limits',
                        min_value=big_data[temps[-1]][1][eje_x].min(),
                        max_value=big_data[temps[-1]][1][eje_x].max(),
                        value =norm_lims_default,
                        #on_change=update_norm_lims,
                        key = 'norm_lims_key',
                        step = (big_data[temps[-1]][1][eje_x].max()-big_data[temps[-1]][1][eje_x].min()) / 100.)


        big_data[temps[-1]][1].plot(x = eje_x, y= 'Heat Flow', ax = ax1, legend = False)
        ax1.axvline(norm_lims[0], color = 'b', linestyle = '--')
        ax1.axvline(norm_lims[1], color = 'b', linestyle = '--')
        norm_indices = big_data[temps[-1]][1][eje_x][
            (big_data[temps[-1]][1][eje_x] >= norm_lims[0])
            & (big_data[temps[-1]][1][eje_x] <= norm_lims[1])
            ].index

        try:
            m = (big_data[temps[-1]][1]['Heat Flow'][norm_indices.max()] - big_data[temps[-1]][1]['Heat Flow'][norm_indices.min()]) / ((big_data[temps[-1]][1][eje_x][norm_indices.max()]-big_data[temps[-1]][1][eje_x][norm_indices.min()]))
            b = big_data[temps[-1]][1]['Heat Flow'][norm_indices.min()] - m * big_data[temps[-1]][1][eje_x][norm_indices.min()]
            norm_ref = b + m * big_data[temps[-1]][1]['t'][norm_indices.min() : norm_indices.max()]
            norm_value = np.trapezoid(big_data[temps[-1]][1]['Heat Flow'][norm_indices.min() : norm_indices.max()] - norm_ref, big_data[temps[-1]][0]["t"][norm_indices.min() : norm_indices.max()])
            #st.write(norm_value)
            cmap = plt.get_cmap('Blues')
            colors = np.linspace(0.3, 1, len(temps))
            for i in range(len(temps)):
                color = cmap(colors[i])
                ints[i][1] = ints[i][1] / norm_value
                ax2.plot(temps[i], ints[i][1], "o", color = color)
        except KeyError:
            st.write('set Tm limits')
           

    if mode == 'FULL':
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
                style=main_color,
                linewidth = 1,
            )
            big_data[i][1].plot(
                x=eje_x,
                y="Heat Flow",
                ax=ax1,
                legend=False,
                style=ref_color,
                linewidth=1.1,
            )

            #   Plot the labels on each curve
            ax1.text(
                big_data[i][0][eje_x].iloc[-1] *1.01,
                big_data[i][0]["Heat Flow"].iloc[-1],
                i,
                fontsize = 10,
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
                    color=shade_color,
                )
            else:
                ax1.fill_between(
                    big_data[i][1][eje_x],
                    big_data[i][0]["Heat Flow"].iloc[
                        : len(big_data[i][1]["Heat Flow"])
                    ],
                    big_data[i][1]["Heat Flow"],
                    color=shade_color,
                )

    #   Clear up the graph, remove borders and y axis
    ax1.spines["top"].set_visible(False)
    ax1.spines["left"].set_visible(False)
    ax1.spines["right"].set_visible(False)
 

    scalebar = sc.add_scalebar(scalebar_scale, ax1, matchx = False, hidex = False, )
    buffer1 = io.BytesIO()
    fig.savefig(buffer1, format='pdf')
    buffer1.seek(0)  # Move the cursor to the start of the buffer
    if mode != 'FULL':
        with inte:
            with st.expander('Integral plot limits', expanded = True):

                # Further divide the space into two columns
                low, up = st.columns(2)
                #   In one column get a text input for the lower plotting limits of integral plot
                with low:
                    lower = st.text_input("Lower Ta limit", key="lower", value="-100")
                    #lower_y = st.text_input("Lower H limit", key="lower_y", value = '0')
                #   In the other for the upper limits
                with up:
                    upper = st.text_input("Upper Ta limit", key="upper", value="300")
                    #upper_y = st.text_input("Upper H limit", key="upper_y", value='0.004')
        ax2.set_xlim((int(lower), int(upper)))
        ax2.set_ylim((float(lower_y), float(upper_y)))  
        ax2.grid(True, axis='x', linestyle = '-.', color = '#eeeeee')
        if mode == "NORMALIZE":
            ax2.set_ylabel(r'$\int_{peak}(Q-Q_{ref})dt\ / \ \sigma_{T_m}$')
        else:
            ax2.set_ylabel(r'$\int_{peak}(Q-Q_{ref})dt$')
        ax2.set_xlabel(r'$T_a\ /\ ^{\degree}C$')
        ax2.ticklabel_format(axis = 'y', style='sci', scilimits = (-2, 2))
                #   Show integral plot

        buffer = io.BytesIO()
        fig2.savefig(buffer, format='pdf')
        buffer.seek(0)
        with inte:
            _, plot_inte, _ = st.columns ([.5, 2, .5])
            with plot_inte:
                st.pyplot(fig2, use_container_width=True)
            _, dwl_ent, name, button, _ = st.columns([.5, .5, 1, .5, .5])

            result_string = '\n'.join(f"{tup[0]}\t{tup[1]}" for tup in ints)
            with dwl_ent:
                st.download_button('download enthalpies', result_string)
            with name:
                inte_name = st.text_input('Save as:', label_visibility='collapsed', placeholder='Integral plot name')
            with button:
                st.download_button(
                        label="Download Integral Plot",
                        data=buffer,
                        file_name=inte_name + '.pdf',
                        mime="image/pdf"
                        )        
    #   Show main graph
    with graf:
        st.pyplot(fig)
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
#except TypeError:
#    with graf:
#        st.markdown('<p class="big-font">Missing File:</p>', unsafe_allow_html=True)
#        for key, (df1, df2) in big_data.items():
#            if df1 is None:
#                st.write('Ta = ', key)
#            if df2 is None:
#                st.write('Ta = ', key, '_ref')
#except KeyError:
#    with graf:
#        st.markdown('<p class="big-font">Upload Files</p>', unsafe_allow_html=True)