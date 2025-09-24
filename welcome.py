import streamlit as st
import base64

with open("Assets/screenshots/annealing_modify.png", "rb") as f:
    img_bytes = f.read()

b64 = base64.b64encode(img_bytes).decode()
src_modify = f"data:image/png;base64,{b64}"

with open("Assets/screenshots/annealing_full.png", "rb") as f:
    img_bytes = f.read()

b64 = base64.b64encode(img_bytes).decode()
src_full = f"data:image/png;base64,{b64}"

with open("Assets/screenshots/step_response.png", "rb") as f:
    img_bytes = f.read()

b64 = base64.b64encode(img_bytes).decode()
src_step_res = f"data:image/png;base64,{b64}"

def welcome():
    st.markdown(f"""
        <div style="font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 0; background-color: transparent;">
            <div style="width: 85%; margin: auto; padding-top: 20px;">
                <div style="font-size: 3em; text-align: center; margin-bottom: 20px;">
                    JM / F-DSC
                </div>
                <div style="font-size: 1.3em; text-align:center; margin-bottom: 20px;">
                    Our Data Processing Tool for Flash Differential Scanning Calorimetry (a.k.a Fast Differential Calorimetry)
                </div>
                <div style="font-size: 1em; text-align: justify;">
                    <p>
                        Welcome! This program is designed to assist with processing data for <span style="font-weight: bold; color: #0073e6;">Flash Differential Scanning Calorimetry</span> (FDSC).
                        You can explore the various tools available by navigating through the tabs at the top of the page.
                        These tabs provide access to different types of measurements we currently support—although please note that most are still a work in progress (WIP).
                    </p>
                    <p>
                        Below, you will find detailed instructions on how to use these tools, as well as information on their capabilities.
                    </p>
                    <p>
                    <ul>
                        <li><b>Kinetics:</b> Reads the data and auto-generates a baseline, then integrates to find the enthalpy. If a temperature list is provided, then it plots enthalpy vs temperature.
                        <li><b>Annealings:</b> Reads all files and automatically detects reference and measurement curves, pairing them by filename. Therefore, file naming is key:<ul>
                                            <li>It must contain the temperature of the previous annealing immediately followed by either 'deg' or 'degree'.
                                            <li>Annealings at temperatures below 0 ºC will be indicated with the word 'minus' before annealing temperature.
                                            <li>Reference curves must have the suffix '_ref' before the file format.
                                            </ul>
                                            Functionality is almost complete. It separates and displays curves to properly inspect them. Allows you to fix overlap with the reference curve and integration limits for the enthalpy curve by curve. It is also posible to export all data, from enthalpies, to overlapped and separated curves and differences with the references.
                        <div style="font-size: 3em; text-align: center; margin-bottom: 20px;">
                            <img src="{src_full}" width=35%>  <img src="{src_modify}" width=58.92%>
                        </div>
                        <li> <b>Coolings:</b> Mostly a quality of life tool to separate cooling measurements containing many curves laid out one after another into different columns.
                        <li> <b>Step Response:</b> As the name says; a tool to process step response experiments to calculate C<sub>p</sub> and separate it into reversing and non-reversing at different frequencies (given by experiment parameters).
                                                <div style="font-size: 3em; text-align: center; margin-bottom: 20px;">
                            <img src="{src_step_res}" width=67.42%> <br>
                        </div>
                    </ul>
                    </p>
               
        </div>
    """, unsafe_allow_html=True)
