import streamlit as st
import hashlib
from io import StringIO
import re
import pandas as pd
import numpy as np
# import warnings



def bubble(bub_color, bub_border, temps_text):
    col1, col2 = st.columns([10, 1])

    with col1:
        sub1, sub2 = st.columns([1, 3])
        with sub2:
            st.markdown(
                f"""
                <div style="
                    background-color:{bub_color};
                    padding:7px 10px;
                    border-radius:10px;
                    border:1px solid {bub_border};
                    color:#000000;
                    font-size:16px;
                    box-shadow:0 1px 2px rgba(0,0,0,0.08);
                ">
                    </b> Temps: </b> {temps_text}
                </div>
                """,
                unsafe_allow_html=True,
            )
        with sub1:
            manual = st.toggle('Manual temps', key='manual')

    with col2:
        if not st.session_state['closed_bubble'] and st.session_state['closable']:
            if st.button("✅", key="close_bubble"):
                st.session_state.show_bubble = False
                st.session_state.closed_bubble = True
    return manual



# Function to compute the hash of file content
def compute_file_hash(file):
    file_content = file.read()
    file.seek(0)  # Reset the file pointer
    return hashlib.md5(file_content).hexdigest(), file_content

def find_temps(filename, n_temps):
    # initialize state
    if "show_bubble" not in st.session_state:
        st.session_state.show_bubble = False
        st.session_state.closed_bubble = False
    if 'close_bubble' in st.session_state:
        if st.session_state.close_bubble:
            st.session_state.closed_bubble = True
    if 'closable' not in st.session_state:
        st.session_state['closable'] = True
    pattern = r'from[^0-9-]*(-?\d+)[^0-9-]+(-?\d+)'
    m = re.search(pattern, filename, re.IGNORECASE)
    st.session_state['show_bubble'] = True
    if m:
        limits = sorted(list(map(int, m.groups())))
        # st.write(filename, "->", tuple(map(int, m.groups())) if m else None)
        interval = (limits[1] - limits[0]) / (n_temps-1)
        int_erval = str(int(interval))

        found = bool(re.search(rf'(?<!\d){int_erval}(?!\d)', filename))
        bub_color = '#e8f4ff' if found else "#fffbc9"
        bub_border = '#9ecbff' if found else "#adad18"

        if 'manual' not in st.session_state:
            st.session_state['manual'] = False

        temps_text = f'From {limits[0]} to {limits[1]} every {interval}ºC' if not st.session_state['manual'] else f'Manually set'

        if (st.session_state.show_bubble and not st.session_state.closed_bubble): 
            manual = bubble(bub_color, bub_border, temps_text)
        elif 'close_bubble' in st.session_state:
            
            if not st.session_state['close_bubble']:
                manual = bubble(bub_color, bub_border, temps_text)

    if (not st.session_state.closed_bubble and m != None):
        if manual:

                option_map = {
                    0: "Intervals",
                    1: "List",
                }
                selection = st.segmented_control(
                    "Mode",
                    options=option_map.keys(),
                    format_func=lambda option: option_map[option],
                    selection_mode="single",
                    default=0
                )
                if selection not in option_map:
                    st.session_state['closable'] = False
                    st.warning('Please select an input method')
                elif option_map[selection] == 'Intervals':
                    cols = st.columns(2)
                    with cols[0]:
                        stemp = st.number_input('Start temp', value = 0)
                    with cols[1]:
                        etemp = st.number_input('Final temp', value = 1000)
                    manual_interval = (etemp - stemp) / (n_temps-1)
                    st.session_state['temps'] = list(np.arange(stemp, etemp+int(manual_interval), manual_interval))
                    try:
                        st.session_state['temps'] = [int(temp) for temp in st.session_state['temps']]
                        st.session_state['closable'] = True
                    except Exception as e:
                        st.write(e)
                    st.session_state['closable'] = True
                    # st.session_state['temps'] = temps
                elif option_map[selection] == 'List':
                    st.session_state['closable'] = False
                    temps = st.text_input(f'List of temps', placeholder='Input temperatures').split()
                    if len(temps) != n_temps:
                        st.warning(f'Missing {n_temps-len(temps)} temperatures')
                        st.session_state['closable'] = False
                    else:
                        try:
                            st.session_state['temps'] = [int(temp) for temp in temps]
                            st.session_state['closable'] = True
                        except Exception as e:
                            st.write(e)
        else:
            temps = list(range(limits[0], limits[1]+int(interval), int(interval)))
            st.session_state['temps'] = temps

    elif not m:

        if (st.session_state.show_bubble and not st.session_state.closed_bubble):
                
                col1, col2 = st.columns([10, 1])
                bub_text = '</b> No temperature Range found in filename</b>'
                bub_color = "#DB5D5D92"
                bub_border = "#B10808D6"
                with col1:


                    st.markdown(
                        f"""
                        <div style="
                            background-color: {bub_color};
                            padding:7px 10px;
                            border-radius:10px;
                            border:1px solid {bub_border};
                            color:#000000;
                            font-size:16px;
                            box-shadow:0 1px 2px rgba(0,0,0,0.08);
                        ">
                            {bub_text}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                if 'temps' in st.session_state and st.session_state.closable:
                    with col2:
                        if not st.session_state['closed_bubble']:
                            if st.button("✅", key="close_bubble"):
                                st.session_state.show_bubble = False
                                st.session_state.closed_bubble = True


                option_map = {
                    0: "Intervals",
                    1: "List",
                }
                selection = st.segmented_control(
                    "Mode",
                    options=option_map.keys(),
                    format_func=lambda option: option_map[option],
                    selection_mode="single",
                    default=0
                )
                if selection not in option_map:
                    st.session_state['closable'] = False
                    st.warning('Please select an input method')
                elif option_map[selection] == 'Intervals':
                    cols = st.columns(2)
                    with cols[0]:
                        stemp = st.number_input('Start temp', value = 0)
                    with cols[1]:
                        etemp = st.number_input('Final temp', value = 1000)
                    manual_interval = (etemp - stemp) / (n_temps-1)
                    st.session_state['temps'] = list(np.arange(stemp, etemp+int(manual_interval), manual_interval))
                    try:
                        st.session_state['temps'] = [int(temp) for temp in st.session_state['temps']]
                        st.session_state['closable'] = True
                    except Exception as e:
                        st.write(e)
                    st.session_state['closable'] = True
                    # st.session_state['temps'] = temps
                elif option_map[selection] == 'List':
                    temps = st.text_input(f'List of temps', placeholder='Input temperatures').split()
                    if len(temps) != n_temps:
                        st.warning(f'Missing {n_temps-len(temps)} temperatures')
                        st.session_state['closable'] = False
                    else:
                        try:
                            st.session_state['temps'] = [int(temp) for temp in temps]
                            st.session_state['closable'] = True
                        except Exception as e:
                            st.write(e)
                    

            
    elif 'temps' not in st.session_state and st.session_state.close_bubble and m != None:
            temps = list(range(limits[0], limits[1]+int(interval), int(interval)))
            st.session_state['temps'] = temps

    temps =st.session_state['temps']

    return temps





def segmentation(file):

    if len(file) == 1:
        file_hash, file_content = compute_file_hash(file[0])
        lines = file_content.decode('latin1').splitlines()
        segment_n = -1
        segments = {}
        chip_name = None
        chip_name_check = False
        for line in lines:
            if chip_name_check:
                chip_name = line.split()[1]
                # st.write(chip_name)
                chip_name_check = False
            if line == '' or '_' in line or '.' in line or '[' in line or 'Index' in line:
                continue
            elif line == 'Curve Name:' and chip_name == None:
                chip_name_check = True
                continue
            elif line == 'Curve Name:':
                continue
            elif line == 'Curve Values:':
                segment_n += 1
                continue

            if segment_n not in segments:
                segments[segment_n] = ''
            segments[segment_n] += line.replace(',', '.') + '\n'

        # st.write(f'Number of temperatures: {(segment_n+1)/2}')
        n_temps = int((segment_n+1)/2)
    else:
        st.write('Upload only ONE (1) file')
    return chip_name, n_temps, segments




def get_big_data(segments, temps, eje_x, t_s, t_end, column):
    big_data = {}
    if len(temps)*2 + 1 == len(list(segments.keys())):
        with column:
            st.warning('One extra segment was found. Ignoring first segment.')
        del segments[list(segments.keys())[-1]]
        # st.write(segments)
    elif len(temps) != (len(list(segments.keys())))/2:
        st.write('Number of temperatures: ', temps)
        st.write('Number of segments: ', len(list(segments.keys())))
        raise KeyError('temps and segments don\'t match')
 
    for i, temp in enumerate(reversed(temps)):
        ref_df = pd.read_csv(StringIO(segments[2*i]), sep='\\s+', dtype=float, names = ['Index', 't', 'Ts', 'Tr', 'Heat Flow'])
        ann_df = pd.read_csv(StringIO(segments[2*i+1]), sep='\\s+', dtype=float, names = ['Index', 't', 'Ts', 'Tr', 'Heat Flow'])

        ref_df = ref_df[ref_df[eje_x].between(t_s, t_end)]
        ann_df = ann_df[ann_df[eje_x].between(t_s, t_end)]

        big_data[temp] = (ann_df, ref_df)
    return big_data