# P.I.P.E. and NUL-plus

PIPE (Pipeline for Interesting Pulsars and maybe E.t.) and NUL-plus are a streamlined pipeline for processing raw filterbank data from the ATA to produce relevant time series for nulling analysis. The core of the analysis is wrapped by PIPE into a user-friendly format, taking care of RFI, Dedispersion, Tempo Corrections, and Folding, essentially out of the box.

# Usage - P.I.P.E.

In the current setup, PIPE takes one .fil file at a time. All relevant inputs are handled in run_pipe.py, where the .fil filepath, working homepath, pulsar name and DM, and other relevant information is inputted in some editor of your choice. To run:

  python run_pipe.py
  
  (pulsar) bash pipe.bash

When running run_pipe.py for the first time, you will see many .bash files and directories pop up - don't worry. The directories are there to handle data as it is being put through the pipeline, and the .bash files represent the individual operations on our data (rfi, dedispersion, etc.). 

Note: you will need to be running in the ATA pulsar conda environment for pipe.bash to work.

pipe.bash will output a lot of diagnostic information as the file is being processed. Ideally there should be no warnings or errors. The final time series can then be located in ./final_asciis/.

# Usage - NullAnalysis.py (Time Series Extraction)

Once you have your final .ascii files produced, you can move them into one directory to extract individual time series on their pulses. This extraction is automated using NullAnalysis.py. Usage is simply:

python NullAnalysis.py {-options}

Before running, make sure to update the directory path in the second line of the file. In the default procedure, it will read through the different files and ask you which node to choose (by index of outputted list). It will then search for any peaks in the summed profile and then extract the "intensity" as measered by the power integral over the pulse width, finally producing a diagnostic plot. This plot is automatically saved and displayed. This allows us to look through at the quality of our processed data. The program then loops until you have looked at all the nodes you wanted to

The options for NullAnalysis.py are:

"-a" : Automatically loops through all nodes one by one

"--nopltsave" : Don't save diagnostic plots

"--nopltshow" : Don't display diagnostic plots

"--asksave" : Ask user if they want to save the extracted time series


Notes on options:

"--asksave" should be used once you are ready to extract time series data.

"-a --nopltshow" automatically loops through all data and saves diagnostics without wasting time displaying the plots.
