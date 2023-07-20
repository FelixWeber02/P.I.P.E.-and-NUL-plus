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

# Usage - Filtering with NullAnalysis.py

Eventhough PIPE takes care of most of the RFI in our data, we will still observe large amounts of background noise, creating fluctuating power levels over time. This can directly interfere with measurements of pulse intensities. When using the "-f" option, NullAnalysis (if there aren't too many peaks) will interpolate the background power levels:

![alt text](https://github.com/FelixWeber02/P.I.P.E.-and-NUL-plus/blob/main/README_Images/Good_Back_Inter.png?raw=true)

Note that the quality of this process is dependant on the fine-tuning paramter "peak_width_2" (float: 0.0 to 1.0) set in the beginning of NullAnalysis.py. This paramter controls how much of the area around the peak is ignored when interpolating the background. Generally speaking, best practice is to lower the value as SNR and/or peak width increase, and to increase it as SNR and/or peak width decreases. The following is an example where peak_width_2 was set to high for an observation:

![alt text](https://github.com/FelixWeber02/P.I.P.E.-and-NUL-plus/blob/main/README_Images/Back_Bad_Iter.png?raw=true)
