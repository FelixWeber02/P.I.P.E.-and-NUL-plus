''' Our Goal is to run a completed process.py file to push full .fil files through the pipeline '''
''' This preps all .bash files in the pipeline that can be run individually or in one full sweep '''

# Felix Weber, 2023

import glob
import os
from sigpyproc.readers import FilReader

## rficlean: -- no longer in use

def RFIClean(fileloc):
        bash_file = open(r'rficlean.bash', 'w')
	#bash_file.write(


## rfifind_maker: 

def rfifinder(path, NUL_home, plot_rfi, int_time):
        file_list = glob.glob(path + "*.fil")
        os.makedirs("masking_and_killing", exist_ok = True)
        home = NUL_home + "masking_and_killing/"
        bash_file = open(r'rfi.bash', 'w')
        bash_file.write("cd masking_and_killing" + "\n")
        for file in file_list:
                mjd = str.split(file,path)[1].split(".fil")[0]
                command = "rfifind " + file + " -time " + str(int_time) + " -o " +  mjd 
                if plot_rfi==True:
                        command += " -xwin"
                #command2 = "python " + "../vishal_code/rfi_filter.py " + " -fil " + file + " -home " + home + " -mask " + mjd + "_rfifind.mask"
                print(command)
                #print(command2)
                bash_file.write(command + "\n")
                #bash_file.write(command2 + "\n")

        bash_file.close()

#New method of dedispersion to include RFI mask

def Prepdata(homepath, path, dm):
        file_list = glob.glob(path + "*.fil")
        os.makedirs("tim_files", exist_ok = True)
        os.makedirs("dat_fils", exist_ok = True)
        bash_file = open(r'Prep.bash', 'w')
        for file in file_list:
                mjd = str.split(file,path)[1].split(".fil")[0]
                command1 = "prepdata -nobary -o " + homepath + "dat_fils/" + mjd + '_output -dm ' + str(dm) + ' -mask ' + homepath + 'masking_and_killing/' + mjd + "_rfifind.mask " + file
                #command15 = "cp dat_fils/" + mjd + '_output.dat dat_fils/' + mjd + '_output'
                command2 = "python ../dat2tim.py " + homepath + "dat_fils/" + mjd + "_output.dat"
                bash_file.write(command1 + "\n")
                #bash_file.write(command15 + "\n")
                bash_file.write("cd dat_fils/" + "\n")
                #bash_file.write("rm " + mjd + '_output.dat \n')
                bash_file.write(command2 + "\n")
                bash_file.write("mv *.tim ../tim_files"+ "\n")
                #bash_file.write("rm *.tim"+ "\n")
        bash_file.close()
        return mjd + "_output.tim"


## Dedispersion:

def dedisperser(homepath, path, dm):
        file_list = glob.glob(path + "*.fil")
        os.makedirs("tim_files", exist_ok = True)
        bash_file = open(r'dd.bash', 'w')
        bash_file.write("cd " + path + '\n')
        for file in file_list:
                mjd = str.split(file,path)[1].split(".fil")[0]
                file_no_path = str.split(file, '/')[-1]
                command = "dedisperse " + file_no_path + " -d " + str(dm) + " > " + homepath + mjd + "_output.tim"
                print(command)
                bash_file.write(command + "\n")
        bash_file.write("cd " + homepath + "\n")
        mover = "mv *.tim tim_files"
        bash_file.write(mover + "\n")
        bash_file.close()
        return mjd + "_output.tim"

## Tempo:

def tempoer(file_path, j_name, site_code, timfile):
        #Part 1: getting the list of .tim files we'll be working with
        tim_list = ["./tim_files/"+timfile] #glob.glob("./tim_files/*.tim")
        file_list = glob.glob(file_path +  "*.fil")

        #Part 2: getting a .par file for the pulsar (will be used for all .tim files)
        os.makedirs("par_files", exist_ok = True)
        bash_file = open(r'tempo.bash', 'w')

        #this is just for color-coding the bash file (this one will be more complicated than the others)
        bash_file.write("#!/bin/bash \n")
        bash_file.write("psrcat -e " + j_name + " > ./par_files/" + j_name + ".par" + "\n")

        os.makedirs("tz_in_files", exist_ok = True)
        os.makedirs("polyco_files", exist_ok = True)        #this is somewhat atemporal, but I need this to happen before the loop later
        bash_file.write("mv *.in tz_in_files\n")
        
        #print(len(file_list))
        
        #Part 3: constructing the tz.in file for the observatory - done separately for each .tim file
        for i in range(0, len(file_list)):
                #print(i)
                file = file_list[i]
                timfile = tim_list[i]
                #nab the info we'll need to construct the tz.in file from the header
                fil = FilReader(file)
                central_freq = fil.header.fch1 + (-1 * fil.header.foff * (fil.header.nchans / 2))
                print(central_freq)
                pulsar_j_code = j_name[1:]
                print(timfile)
                mjd = str.split(timfile,"/")[-1].split("_")[1]
                print(mjd)
                mjd2 = str.split(timfile, "/")[-1].split("_")[2]
                mjd2_float = float(mjd2)/86400
                mjd2 = str(mjd2_float)[2:]
                print(float(mjd) +  mjd2_float)
                full_mjd_str = mjd + '_' +  mjd2
                full_mjd_float = float(mjd + '.' + mjd2)

                #open and write the tz.in file
                tz_filename = 'tz' + str(i) + '.in'
                tz_file = open(tz_filename, 'w')
                tz_file.write(str(site_code) + " 5 30 12 610\n")
                tz_file.write("\n")
                tz_file.write("\n")
                tz_file.write(pulsar_j_code + " 30 12 5 " + str(central_freq))
                tz_file.close()

                #tell it to copy in and rename the file you want to use
                bash_file.write('cp ./tz_in_files/' + tz_filename + ' tz.in\n')
                bash_file.write("tempo -f ./par_files/" + j_name + ".par -z << EOD\n")
                bash_file.write(str(full_mjd_float - 1) + ' ' + str(full_mjd_float + 1) + '\n')
                bash_file.write('EOD\n')

                #move and rename polyco.dat
                bash_file.write('mv polyco.dat ./polyco_files/' + full_mjd_str + '_polyco.dat')
        bash_file.close()



## Folding!!

def folder(fileloc, timfile):
        obs = fileloc.split(sep='/')[-2]
        file_list = ["./tim_files/"+timfile] #glob.glob("./tim_files/*.tim")
        os.makedirs("final_asciis", exist_ok = True)
        bash_file = open(r'fold.bash', 'w')
        for timfile in file_list:
                mjd = str.split(timfile, '/')[-1].split(".tim")[0].split("_")[1]
                mjd2 = str.split(timfile, '/')[-1].split(".tim")[0].split("_")[2]
                mjd2_float = float(mjd2)/86400
                mjd2 = str(mjd2_float)[2:]
                print(mjd + '_' +  mjd2)
                full_mjd = mjd + '_' +  mjd2
                polyco_file = full_mjd + '_polyco.dat'
                command = "/home/sonata/src/bl_sigproc/src/fold -p ./polyco_files/" + polyco_file + ' ' + timfile + " -n 1024 -d 1 > ./final_asciis/" + full_mjd + "." + obs + "." +  "_output.sp.ascii"
                print(command)
                bash_file.write(command + "\n")
        bash_file.close()


def bash_prep(fileloc, NUL_home, DM, pulsar, sitenum, plot_rfi, int_time):
    rfifinder(fileloc, NUL_home, plot_rfi, int_time)
    timfile = Prepdata(NUL_home, fileloc, DM) #dedisperser(NUL_home, fileloc , DM)
    tempoer(fileloc, pulsar, sitenum, timfile)
    folder(fileloc, timfile)
