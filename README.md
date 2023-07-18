# P.I.P.E. and NUL-plus

PIPE (Pipeline for Interesting Pulsars and maybe E.t.) and NUL-plus are a streamlined pipeline for processing raw filterbank data from the ATA to produce relevant time series for nulling analysis. The core of the analysis is wrapped by PIPE into a user-friendly format, taking care of RFI, Dedispersion, Tempo Corrections, and Folding, essentially out of the box.

# Usage

In the current setup, PIPE takes one .fil file at a time. All relevant inputs are handled in run_pipe.py, where the .fil filepath, working homepath, pulsar name and DM, and other relevant information is inputted in some editor of your choice. To run:

  python run_pipe.py
  (pulsar) bash pipe.bash

When running run_pipe.py for the first time, you will see many .bash files and directories pop up - don't worry. The directories are there to handle data as it is being put through the pipeline, and the .bash files represent the individual operations on our data (rfi, dedispersion, etc.). 

Note: you will need to be running in the ATA pulsar conda environment for pipe.bash to work.

pipe.bash will output a lot of diagnostic information as the file is being processed. Ideally there should be no warnings or errors. The final time series can then be located in ./final_asciis/.
