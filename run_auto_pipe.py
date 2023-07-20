from CompleteProcess import bash_prep
import glob
import os

#############################################################################################


filepath = '/mnt/buf0/PulsarNulling/J0953+0755/fil_60138_81382_822841735_J0953+0755_0001/'

NUL_home = '/mnt/buf0/PulsarNulling/NUL+/'

DM = 2.96927 

pulsar = 'J0953+0755'

plot_rfi = False

int_time = 0.05  # this is the integration time for RFI. For high resolution data, this should be <= 0.1 s

sitenum = 9     # set to 9 if ATA obs - otherwise ask someone who knows TEMPO


##############################################################################################


node_list = glob.glob(filepath+"/*/*.fil")

print(node_list)

print("Nodes available:")

for node in node_list:
    print(node.split(sep='/')[-2])

for node in node_list:
    print("##############################################################################################")
    print("running ", node.split(sep='/')[-2])
    suffix = node.split(sep='/')[-1]
    nodefile = node.removesuffix(suffix)
    #print(nodefile)
    bash_prep(nodefile, NUL_home, DM, pulsar, sitenum, plot_rfi, int_time)
    os.system("bash pipe.bash")
