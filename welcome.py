import streamlit as st

full_ratio = 2250/3750
modify_ratio = 2250/3750
step_ratio = 2764/1382

left_width = 0.6*full_ratio/(full_ratio+modify_ratio)
right_width = 0.6*modify_ratio/(full_ratio+modify_ratio)
step_width = 0.85*step_ratio/(full_ratio+step_ratio)

step_margin = (1. - step_width)/2

def welcome():


    st.markdown(f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: transparent;">
            <div style="width: 85%; margin: auto; padding-top: 20px;">
                <div style="font-size: 3em; text-align: center; margin-bottom: 20px; margin-top: -100px">
                    FFFDSC
                </div>
                <div style="font-size: 1.3em; text-align:center; margin-bottom: 20px;">
                    Our Data Processing Tool for Flash Differential Scanning Calorimetry (a.k.a Fast Differential Calorimetry)
                </div>
                <div style="font-size: 1em; text-align: justify;">
                    <p>
                        Welcome! This program is designed to assist with processing data for <span style="font-weight: bold; color: #0073e6;">Flash Differential Scanning Calorimetry</span> (FDSC).
                        You can explore the various tools available by navigating through the tabs in the sidebar (expand in the top left).
                        These tabs provide access to different types of measurements we currently support—although please note that most are still a work in progress (WIP).
                    </p>
                    <p>
                        Below, you will find detailed instructions on how to use these tools, as well as information on their capabilities.
                    </p>
                    <p>
                    <ul>
                        <li><b>Annealings:</b> Reads all files and automatically detects reference and measurement curves, pairing them by filename. Therefore, file naming is key:<ul>
                                            <li>It must contain the temperature of the previous annealing immediately followed by either 'deg' or 'degree'.
                                            <li>Annealings at temperatures below 0 ºC will be indicated with the word 'minus' before annealing temperature or a '-'.
                                            <li>Reference curves must have the suffix '_ref' or 'Referencia' before the file format.
                                            </ul><p>
                                            Functionality is almost complete. It separates and displays curves to properly inspect them. Allows you to fix overlap with the reference curve and integration limits for enthalpy calculation curve by curve. It is also posible to export all data, from enthalpies, to overlapped and separated curves and differences with the references.
                                            Now, you can also save your progress with the analysis using the <b>save_state</b> feature. This will download a .json file you can then reupload along with your files to get the sliders back to where you had them.</p><p>
                        </p><p>
                        <b>TODO:</b> Working towards adding a couple of features:<ul>
                            <li>    Single File Upload: I know saving the files individually is a pain, so im working to save you time by making the program auto-detect them for you.
                            <li>    It would be nice if you could input a colormap name instead of using three color inputs for the gradient, working on that.
                            </ul></p>
                    </ul>
                    </p>
               
        </div>
    """, unsafe_allow_html=True)

    _, left,center, right, _ = st.columns([0.2, left_width, left_width, right_width,0.2], gap='small')
    with left:
        st.image("static/screenshots/annealings_FULL.png", caption = 'Example separated curves')
    with center:
        st.image("static/screenshots/annealings_diff.png", caption = 'Example of separated differences to the reference')
    with right:
        st.image("static/screenshots/annealings_ints.png", caption = 'Enthalpies calculated from the example curves')
    
    #   Step Response
    st.markdown('''
                <div style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: transparent;">
                    <div style="width: 85%; margin: auto; padding-top: 5px;">
                        <div style="font-size: 1em; text-align: justify;">
                            <ul>
                                <li> <b>Step Response:</b>  As the name says; a tool to process step response experiments to calculate Cp and separate it into reversing and non-reversing at different frequencies (given by experiment parameters).
                            </ul>
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)
    _, right, _ = st.columns([step_margin, step_width, step_margin])
    with right:
        st.image("static/screenshots/step_response.png", caption = 'Example of a processed step response experiment.')
    
    st.markdown('''
                <div style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: transparent;">
                    <div style="width: 85%; margin: auto; padding-top: 5px;">
                        <div style="font-size: 1em; text-align: justify;">
                            <ul>
                                <li> <b>Kinetics:</b> Reads the data and auto-generates a baseline, then integrates to find the enthalpy. If a temperature list is provided, then it plots enthalpy vs temperature.<p>
                                    <b>TODO:</b><ul>
                                        <li> Add cumulative integration to make S-like plots and fit to either Malkin or Avrami isothermal crystallization model.
                                        </ul>
                                    </p>
                                <li> <b>Coolings:</b> Mostly a quality of life tool to separate cooling measurements containing many curves laid out one after another into different columns.
                            </ul>
                        </div>
                    </div>
                </div>
                ''', unsafe_allow_html=True)