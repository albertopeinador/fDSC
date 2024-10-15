#  Flash DSC
A web app to process your flash-DSC data.
##  Introduction
Flash DSC (flash differencial scanning calirometry) is an ultra-fast characterization technique used in several fileds of reasearch. This web app has been developed with polymer characterization in mind.
It is a deployed Streamlit web app meaning it can be run on any web browser by going to `fdscwip.streamlit.app` without the need to download or intall anything. The deployment is currently set private. So if you need to use this app feel free to contact me to request permission. Otherwise it can be run locally following the steps listed below.
##  Running the app localy
First you will need to install python and the needed dependencies. There are plenty of tutorials online on how to do this.
The dependencies the program uses are the following:
+ >streamlit
+ >matplotlib
+ >numpy
+ >pandas

You can download the code from this directory. Then open a terminal window in the downloaded folder and run `streamlit run fdsc.py`. If it doesnt recognize streamlit as a command then you have not added your pyhton directory to PATH.

Alternatively you can use `python -m streamlit run fdsc.py`. The app should open in a new tab in your default browser.
##  Using the app
The app can be used to process many types of fdsc data. However, it will work best and be the most intuitive for its intended porpouse: polymer characterization.

The first thing you will notice is you will have to upload the output files. The files should have a specific pattern in the file name for them to be recognized.
As it stands it tries to find the annealing temperatur in the file name (again, polymer characterization in mind) between a underscore and either the word `degree` or `deg`. For some legacy reasons the program will also ignore files with this pattern that end in `_modified`. If the annealing temperature is negative it should be noted with the word `minus` after the underscore and the number itself.

Two files are expected for each annealing temperature: the measurement and the baseline. The second should be noted by adding `_ref` at the end of the file name.

After that all controls should be fairly intuitive.

Note some limitations of the app.
+ The x axis should be selected at the begining, otherwise changes to the integration limits will be lost, as they will be recalculated to be in the correct domain.
+ If you go back and select a previously modified curve, it will reset the changes made to that curve. This will happen even when you go back to the `MODIFY` mode after normalizing or checking out the `FULL` plot, **the changes to the first curve will be reset if you do this**.

##  Credit
Huge credit goes to GitHub user dmeliza for the code relating to the vertical scalebar. I have modified it slightly, but it is essencially their code.
