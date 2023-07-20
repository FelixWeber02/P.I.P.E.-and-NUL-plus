# P.I.P.E. and NUL-plus

PIPE (Pipeline for Interesting Pulsars and maybe E.t.) and NUL-plus are a streamlined pipeline for processing raw filterbank data from the ATA to produce relevant time series for nulling analysis. The core of the analysis is wrapped by PIPE into a user-friendly format, taking care of RFI, Dedispersion, Tempo Corrections, and Folding, essentially out of the box. Note: intended mostly for use on ATA servers (PIPE) and personal machines (NullAnalysis.py)

# Usage - P.I.P.E. (.fil Processing)

In the current setup, PIPE can take one .fil file at a time, or a full observation batch. 

To run one .fil at a time, we will be using run_pipe.py. All relevant inputs are handled in run_pipe.py, where the .fil filepath, working homepath, pulsar name and DM, and other relevant information is inputted in some editor of your choice. To run:

  python run_pipe.py
  
  (pulsar) bash pipe.bash

When running run_pipe.py for the first time, you will see many .bash files and directories pop up - don't worry. The directories are there to handle data as it is being put through the pipeline, and the .bash files represent the individual operations on our data (rfi, dedispersion, etc.). 

Note: you will need to be running in the ATA pulsar conda environment for pipe.bash to work.

pipe.bash will output a lot of diagnostic information as the file is being processed. Ideally there should be no warnings or errors. The final time series can then be located in ./final_asciis/.

To run a full observation batch, we can use run_auto_pipe.py. Opening it up, you will see that the inputs are nearly identitical, however instead of requiring a directory with one .fil, it requires the path for the observation directory (the one with all the LoB/LoC folders). Once putting in the right inputs, you can run it using:

(pulsar) python run_auto_pipe.py

This will automatically loop through all nodes, generating and running each respective .fil files through PIPE, one by one. The program will end once all nodes available have been processed. This is most useful with long observations. 

Note: before running run_auto_pipe.py make sure you have removed any nodes that you know don't contain any pulses or have way too much RFI (usually LoC nodes) - you will save precious time this way.

# Usage - NullAnalysis.py (Time Series Extraction)

Once you have your final .ascii files produced, you can move them into one directory to extract individual time series on their pulses. This extraction is automated using NullAnalysis.py. Usage is simply:

python NullAnalysis.py {-options}

Before running, make sure to update the directory path in the second line of the file. In the default procedure, it will read through the different files and ask you which node to choose (by index of outputted list). It will then search for any peaks in the summed profile and then extract the "intensity" as measered by the power integral over the pulse width, finally producing a diagnostic plot. This plot is automatically saved and displayed. This allows us to look through at the quality of our processed data. The program then loops until you have looked at all the nodes you wanted to

The options for NullAnalysis.py are:

"-a" : Automatically loops through all nodes one by one

"-c" : Compile selected nodes for a complete time series

"-f" : Filter out background noise/rfi

"--nopltsave" : Don't save diagnostic plots

"--nopltshow" : Don't display diagnostic plots

"--asksave" : Ask user if they want to save the extracted time series

"--timeseries" : Loops through all .fil files and only produces time series (no plotting, and will ask to save for RFI-heavy files)


Notes on options:

"--asksave" should be used once you are ready to extract time series data.

"-a --nopltshow" automatically loops through all data and saves diagnostics without wasting time displaying the plots.

Diagnostic plots produced by NullAnalysis.py will look like this for each individual node:
![alt text](https://github.com/FelixWeber02/P.I.P.E.-and-NUL-plus/blob/main/README_Images/J1136+1551_clean_LoB.C1312_Diagnostic.png?raw=true)
The full red lines will show what is being summed for peak intensities and the dashed red line is the base power level used for peak searches. This is useful to diagnose SNR and quality of the data in question.

# Usage - Filtering with NullAnalysis.py (-f)

Eventhough PIPE takes care of most of the RFI in our data, we will still observe large amounts of background noise, creating fluctuating power levels over time. This can directly interfere with measurements of pulse intensities. When using the "-f" option, NullAnalysis (if there aren't too many peaks) will interpolate the background power levels:

![alt text](https://github.com/FelixWeber02/P.I.P.E.-and-NUL-plus/blob/main/README_Images/Good_Back_Inter.png?raw=true)

Note that the quality of this process is dependant on the fine-tuning paramter "peak_width_2" (float: 0.0 to 1.0) set in the beginning of NullAnalysis.py. This paramter controls how much of the area around the peak is ignored when interpolating the background. Generally speaking, best practice is to lower the value as SNR and/or peak width increase, and to increase it as SNR and/or peak width decreases. The following is an example where peak_width_2 was set to high for an observation (peak_width_2 = 0.95):

![alt text](https://github.com/FelixWeber02/P.I.P.E.-and-NUL-plus/blob/main/README_Images/Back_Bad_Iter.png?raw=true)

Setting peak_width_2 = 0.8 we improve the interpolation:

![alt text](https://github.com/FelixWeber02/P.I.P.E.-and-NUL-plus/blob/main/README_Images/Back_Good_Iter.png?raw=true)

Note, we are trying to remove low-frequency fluctiations in the background, so there will usually still be some small fluctiations present in the extracted pulses, however our SNR is now much higher. The rule of thumb here is that the area in the extracted background where we interpolated shouldn't look *too* different from the rest of the background. 

The reason why this parameter is important is because ideally we want to interpolate over as few data points as possible, while also not allowing pulse intensity changes to impact our measurement of the background. The smaller peak_width_2 is, the fewer points we are ignoring, but the more likely we are to include pulse fluctiations into our interpolation. Therefore finding the right balance is critical. Future versions may include a progamatic tuning system for this based on pulse height, width and overall SNR. After filtering diagnostic plots will look like the following:
![alt text](https://github.com/FelixWeber02/P.I.P.E.-and-NUL-plus/blob/main/README_Images/J0953+0755_2_LoB.C1312_Diagnostic.png?raw=true)
Note: the green dashed lines represent the locations where the pulses were removed for background interpolation.

# Usage - Compiling Time Series with NullAnalysis.py (-c)

When using the compilation option (-c), after processing a node, NullAnalysis.py will ask if you want to compile the given node. If you choose yes, it will save the peak profiles in the outlined red regions (as seen in the diagnostics) and sum them together for a complete pulse intensity time series. It will also plot a side by side of every chosen node, hopefully displaying common bright and nulling spots across all nodes:  
![alt text](https://github.com/FelixWeber02/P.I.P.E.-and-NUL-plus/blob/main/README_Images/J0953+0755_2_compiled_diagnostic.png?raw=true)
This is useful as a final sanity check to see if there are any major blips in a node that haven't been removed. After plotting the program will ask to save the final compiled time series as well.

