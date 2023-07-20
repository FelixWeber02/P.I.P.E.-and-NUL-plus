# Necessary Information
path = '../Data/J0953+0755/'

# Fine Tuning:
peak_width_1 = 0.5
peak_width_2 = 0.8

''' The fine tuning arguments should be modified when peak extraction or background filtering is not ideal. 
peak_width_1 sets how much of the peak is being read for peak intensity extraction. 
peak_width_2 sets how much of the pulse area is ignored when filtering the background. 
peak_width_2 should always be bigger than peak_width_1. Generally speaking, peak_width_2 should be decreased the wider 
the pulse and the higher the SNR is. Ideally, when viewing the filtering diagnostics, the extracted pulses should 
show little to no background fluctuations, while the extracted background should show minimal tampering where the pulses were removed.'''

#importing standard packages
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.scale as scale
import numpy.random as rand
import scipy.stats
import scipy.ndimage as nd
import glob
import scipy.signal as sig
import scipy.interpolate as intp
import sys
import argparse
parser = argparse.ArgumentParser()

#importing kaplan code
import kaplan_source as nulling_mcmc
import kaplan_output_maker as kaplan

parser.add_argument("-a", help="To Loop over all", const=True, default=False, action='store_const')
parser.add_argument("-t", "--timeseries", help="Only extract time series of all .fil files in the directory", const=True, default=False, action='store_const')
parser.add_argument("-c", "--compile", help="Ask which nodes are good and then compile them", const=True, default=False, action='store_const')
parser.add_argument("-f", "--filter", help="subtract background noise from found pulse", const=True, default=False, action='store_const')
parser.add_argument("--nopltsave", help="Don't save plots", const=True, default=False, action='store_const')
parser.add_argument("--nopltshow", help="Don't show plots", const=True, default=False, action='store_const')
parser.add_argument("--asksave", help="Ask if to save Pulse Intensities", const=True, default=False, action='store_const')

args = parser.parse_args()

All = args.a

plt.rcParams.update({'font.size': 8})

if args.timeseries == True:
    All = True
    args.nopltsave = True
    args.nopltshow = True
    args.asksave = True


# Now the fun begins:
file_list = glob.glob(path + "*.ascii")
file_list.sort()
pulsar = path.split(sep='/')[-2]

print("Looking at Pulsar: ", pulsar)
print("Number of Files = ", len(file_list))

nodes = []
good_nodes = []
good_extracts = []

for filename in file_list:
    node_int = filename.split(sep='._output.')[0].split(sep='.')
    node = node_int[-2] + '.' + node_int[-1]
    nodes.append(node)

#nodes.sort() 

print("Nodes in Available: ", nodes)

if All == False:
    print("Which index to choose? Enter 'n' once done")
    In = input()
elif All == True:
    print("Looping Through All Nodes")
    In = 0

while In != 'n':
    index = int(In)
    node = nodes[index]
    file = open(file_list[index])

    print("Node chosen: ", node)


    data =  file.read().splitlines()

    number_of_phases_plus_header = 1025
    number_of_pulses = int(len(data)/number_of_phases_plus_header)
    print("# of Pulses = ", number_of_pulses)

    reshaped_data = np.reshape(data,(number_of_pulses,number_of_phases_plus_header))

    all_pulse_array = []
    for i in range(0,number_of_pulses):
        pulse = reshaped_data[i]
        pulse_data = pulse[1:]
        float(pulse_data[0].split(sep = ' ')[1])
        final_pulse = [] 

        for item in pulse_data:
            temp = float(item.split(sep = ' ')[1])
            final_pulse.append(temp)
        all_pulse_array.append(final_pulse)

    np.shape(all_pulse_array)

    all_pulse_array = np.array(all_pulse_array)

    #Plotting Pulses over time

    filt_array =  all_pulse_array #G_pulse_array

    #print(node)

    filt_array = nd.gaussian_filter(filt_array, sigma=[4,8])#[:,800:875]

    sum_curve = np.sum(filt_array, axis=0)

    # Pulse Loc finder

    fact = 0.3

    res = sig.find_peaks(sum_curve, height = fact * (np.max(sum_curve)-np.min(sum_curve)) + np.min(sum_curve))

    print("Peak Locations: ", res[0])

    Peak_Locs = res[0]

    res = sig.peak_widths(sum_curve, Peak_Locs, rel_height=peak_width_1)
    
    extract = filt_array[:,int(res[2][0]):int(res[3][0])]
    
    if (args.filter == True) and (len(Peak_Locs) < 3):

        print("Filtering...")
        
        res2 = sig.peak_widths(sum_curve, Peak_Locs, rel_height=peak_width_2)

        background_1 = filt_array[:,int(res2[2][0])-int(res[0][0]):int(res2[2][0])]
        background_2 = filt_array[:,int(res2[3][0]):int(res2[3][0])+int(res[0][0])]
        extract2_shape = np.shape(filt_array[:,int(res2[2][0]):int(res2[3][0])])

        background_1_x = np.linspace(1,np.shape(background_1)[1],np.shape(background_1)[1])
        background_2_x = np.linspace(1,np.shape(background_2)[1],np.shape(background_2)[1]) + int(res[0][0]) + int(res2[0][0])

        background = np.concatenate((background_1, background_2), axis=1)
        background_x = np.concatenate((background_1_x, background_2_x))
        background_pulses = np.linspace(1,number_of_pulses, number_of_pulses)
        background_x, background_pulses = np.meshgrid(background_x, background_pulses)
        
        #print(np.shape(background), np.shape(background_x))
        
        background_on_pulse_x = np.linspace(np.shape(background_1)[1], np.shape(background_1)[1] + extract2_shape[1]-1, extract2_shape[1])

        background_on_pulse = []
        
        for i, row in enumerate(background):
            f = intp.interp1d(background_x[i],row, kind='slinear')
            background_on_pulse.append(f(background_on_pulse_x))
        
        background_on_pulse = np.array(background_on_pulse)
        
        full_back = np.concatenate((filt_array[:,:int(res2[2][0])],background_on_pulse,filt_array[:,int(res2[3][0]):]), axis=1)
        
        filt_array -= full_back
        
        fig, axs = plt.subplots(1,2, figsize=(16,8), sharey='row')
        
        axs[0].set_title("Extracted Background: " + pulsar + " " + node)
        axs[0].imshow(full_back, aspect='auto')
        axs[0].set_xlabel("Relative Phase index / 1024")
        axs[0].set_ylabel("Pulse #")
        
        axs[1].set_title("Extracted Pulses " + pulsar + " " + node)
        axs[1].imshow(filt_array, aspect='auto')
        axs[1].set_xlabel("Relative Phase index / 1024")
        
        plt.show()
    
    elif (args.filter == True):
        print("Too many peaks to filter, check RFI")
    
    print("Now creating diagnostics")
    

    if len(Peak_Locs) < 3:
        sum_time_curve = np.sum(extract, axis=1)
    else: 
        sum_time_curve = np.sum(filt_array, axis=1)
        print("Too Many Peaks, Check RFI")

    fig, axs = plt.subplots(2,2, figsize=(9,9), sharex='col')    
        
    #axs[0,0].set_figsize((7,7))
    if args.filter == True:
        axs[0,0].set_title(pulsar + " - " + node + " Filtered")
    else:
        axs[0,0].set_title(pulsar + " - " + node)
    axs[0,0].imshow(filt_array, norm='linear', aspect='auto', interpolation='none', vmax=2*np.max(sum_curve)/1000, vmin=1*np.min(sum_curve)/1000)
    #plt.ylim((0,50000))
    #plt.xlim((800,875))
    #plt.colorbar(label = "Relative Intensity")
    axs[0,0].set_xlabel("Relative Phase index / 1024")
    axs[0,0].set_ylabel("Pulse #")
    if len(Peak_Locs) < 3:
        for loc in res[2:]:
            axs[0,0].axvline(loc[0], color='r', linestyle='-')
        if args.filter == True:
            for loc in res2[2:]:    
                axs[0,0].axvline(loc[0], color='g', linestyle='--')

    #axs[0,1].set_figsize((7,7))
    axs[1,0].set_title(pulsar + " Summed Pulse Profile")
    axs[1,0].plot(sum_curve)
    axs[1,0].plot(sig.wiener(sum_curve,mysize=50), color='g')
    axs[1,0].set_xlabel("Relative Phase index / 1024")
    axs[1,0].set_ylabel("Summed Intensity")
    axs[1,0].axhline(fact * (np.max(sum_curve)-np.min(sum_curve)) + np.min(sum_curve), color='r', linestyle='--')
    for peak in Peak_Locs:
        axs[1,0].axvline(peak, color='r', linestyle='--')
    for loc in res[2:]:
        axs[1,0].axvline(loc[0], color='r', linestyle='-')
    if (args.filter == True) and (len(Peak_Locs) < 3):
        for loc in res2[2:]:    
            axs[1,0].axvline(loc[0], color='g', linestyle='--')

    #axs[1,0].set_figsize((7,7))
    if len(Peak_Locs) < 3:
        axs[0,1].set_title(pulsar + " Pulse Intensity for 1st Peak")
    else: 
        axs[0,1].set_title(pulsar + " Full Pulse Intensity")
    axs[0,1].scatter(sum_time_curve[::-1],np.linspace(len(sum_time_curve),1,len(sum_time_curve)), marker='x', s=2)
    axs[0,1].set_xscale("log")
    axs[0,1].set_ylabel("Pulse #")
    axs[0,1].set_xlabel("Summed Intensity")
    axs[0,1].invert_yaxis()
    axs[0,1].margins(y=0)

    axs[1,1].set_title(pulsar + " Intensity Distribution")
    axs[1,1].hist(sum_time_curve, density=False, log=False, histtype='step',  bins=10**np.linspace(3,8,100))
    #axs[1,1].set_yscale("symlog")
    #axs[1,1].set_xscale("log")
    axs[1,1].set
    axs[1,1].set_xlabel("Summed Intensity")
    axs[1,1].set_ylabel("Counts")

    if args.nopltsave == False:
        plt.savefig(pulsar + "_" + node +"_Diagnostic.png")
    if args.nopltshow == False:
        plt.show()
    else:
        plt.close()
    
    if args.asksave == True:
        if (args.timeseries == True) and (len(Peak_Locs) < 3):
            ans = 'y'
        else:
            print("Do you want to save this pulse intensity time series? (y/n)")
            ans = input()
        if ans == 'y':
            Data = ''
            for n in sum_time_curve:
                Data += str(float(n)) + ' '
            datafile = open(pulsar+"_"+node+"_Intensities.txt", 'w')
            datafile.write(Data)
            datafile.close()
    
    if args.compile == True:
        print("Do you want to compile this node? (y/n)")
        ans = input()
        if ans == 'y':
            good_nodes.append(index)
            good_extracts.append(extract)
    
    if All == False:
        print("Which index to choose? Enter 'n' once done")
        In = input()
    elif (All == True) and (In < len(nodes) - 1):
        print("Looking at Next Node")
        In += 1
    else:
        In = 'n'

if (args.compile == True) and (len(good_nodes) > 0):
    print('Nodes to Compile:')
    for N in good_nodes:
        print(N)
    compiled_data = np.concatenate(good_extracts, axis=1)
    widths = []
    for dataset in good_extracts:
        widths.append(np.shape(dataset)[1])
    widths[0] = int(widths[0]/2.0)
    
    #print(np.shape(compiled_data))
    
    plt.rcParams.update({'font.size': 9})
    
    fig, axs = plt.subplots(1,2, figsize=(16,8))
    
    axs[0].set_title(pulsar + " Extracts")
    axs[0].imshow(compiled_data, norm='linear', aspect='auto', interpolation='none', vmax=1*np.max(compiled_data), vmin=1*np.min(compiled_data))
    axs[0].set_ylabel("Pulse #")
    axs[0].set_xticks(np.cumsum(widths))
    axs[0].set_xticklabels(np.array(nodes)[np.array(good_nodes)])
    #axs[0].margins(y=0)
    
    sum_time_curve = np.sum(compiled_data, axis=1)
    
    axs[1].set_title("Compiled Time Series")
    axs[1].plot(sum_time_curve, np.linspace(1,len(sum_time_curve),len(sum_time_curve)), marker='x', linewidth=1, color='k')
    axs[1].set_xscale("linear")
    axs[1].set_ylabel("Pulse #")
    axs[1].invert_yaxis()
    axs[1].margins(y=0)
    
    plt.savefig(pulsar+"_compiled_diagnostic.png")
    plt.show()
    
    print("Do you want to save this compiled time series? (y/n)")
    ans = input()
    
    if ans == 'y':
        Data = ''
        for n in sum_time_curve:
            Data += str(float(n)) + ' '
        datafile = open(pulsar+"_compiled_Intensities.txt", 'w')
        datafile.write(Data)
        datafile.close()
    
    
    
