from CompleteProcess import bash_prep

fileloc = '/mnt/buf0/PulsarNulling/fil_60122_84453_738654174_J1136+1551_0001/LoB.C0928/'

NUL_home = '/mnt/buf0/PulsarNulling/NUL+/'

DM = 4.84066 

pulsar = 'J1136+1551'

plot_rfi = False

int_time = 0.05  # this is the integration time for RFI. For high resolution data, this should be <= 0.1 s

sitenum = 9     # set to 9 if ATA obs - otherwise ask someone who knows TEMPO

bash_prep(fileloc, NUL_home, DM, pulsar, sitenum, plot_rfi, int_time)
