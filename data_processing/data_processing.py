# data_processing.py
# Include necessary imports
import uproot
import awkward as ak
import vector
import numpy as np
import time

import sys
import os

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Get the parent directory
parent_dir = os.path.dirname(script_dir)

# Add the parent directory to sys.path
sys.path.append(parent_dir)
import infofile



# Include global variables such as lumi, tuple_path, samples, MeV, and GeV
#lumi = 0.5 # fb-1 # data_A only
#lumi = 1.9 # fb-1 # data_B only
#lumi = 2.9 # fb-1 # data_C only
#lumi = 4.7 # fb-1 # data_D only
lumi = 10 # fb-1 # data_A,data_B,data_C,data_D

fraction = 1.0 # reduce this is if you want the code to run quicker
                                                                                                                                  
#tuple_path = "Input/4lep/" # local 
tuple_path = "https://atlas-opendata.web.cern.ch/atlas-opendata/samples/2020/4lep/" # web address

samples = {

    'data': {
        'list' : ['data_A','data_B','data_C','data_D'],
    },

    r'Background $Z,t\bar{t}$' : { # Z + ttbar
        'list' : ['Zee','Zmumu','ttbar_lep'],
        'color' : "#6b59d3" # purple
    },

    r'Background $ZZ^*$' : { # ZZ
        'list' : ['llll'],
        'color' : "#ff0000" # red
    },

    r'Signal ($m_H$ = 125 GeV)' : { # H -> ZZ -> llll
        'list' : ['ggH125_ZZ4lep','VBFH125_ZZ4lep','WH125_ZZ4lep','ZH125_ZZ4lep'],
        'color' : "#00cdff" # light blue
    },

}

MeV = 0.001
GeV = 1.0

def calc_weight(xsec_weight, events):
    return (
        xsec_weight
        * events.mcWeight
        * events.scaleFactor_PILEUP
        * events.scaleFactor_ELE
        * events.scaleFactor_MUON 
        * events.scaleFactor_LepTRIGGER
    )

def get_xsec_weight(sample):
    info = infofile.infos[sample] # open infofile
    xsec_weight = (lumi*1000*info["xsec"])/(info["sumw"]*info["red_eff"]) #*1000 to go from fb-1 to pb-1
    return xsec_weight # return cross-section weight


def calc_mllll(lep_pt, lep_eta, lep_phi, lep_E):
    # construct awkward 4-vector array
    p4 = vector.zip({"pt": lep_pt, "eta": lep_eta, "phi": lep_phi, "E": lep_E})
    # calculate invariant mass of first 4 leptons
    # [:, i] selects the i-th lepton in each event
    # .M calculates the invariant mass
    return (p4[:, 0] + p4[:, 1] + p4[:, 2] + p4[:, 3]).M * MeV


# cut on lepton charge
# paper: "selecting two pairs of isolated leptons, each of which is comprised of two leptons with the same flavour and opposite charge"
def cut_lep_charge(lep_charge):
    # throw away when sum of lepton charges is not equal to 0
    # first lepton in each event is [:, 0], 2nd lepton is [:, 1] etc
    return lep_charge[:, 0] + lep_charge[:, 1] + lep_charge[:, 2] + lep_charge[:, 3] != 0

# cut on lepton type
# paper: "selecting two pairs of isolated leptons, each of which is comprised of two leptons with the same flavour and opposite charge"
def cut_lep_type(lep_type):
    # for an electron lep_type is 11
    # for a muon lep_type is 13
    # throw away when none of eeee, mumumumu, eemumu
    sum_lep_type = lep_type[:, 0] + lep_type[:, 1] + lep_type[:, 2] + lep_type[:, 3]
    return (sum_lep_type != 44) & (sum_lep_type != 48) & (sum_lep_type != 52)


def read_file(path, sample, start_index, end_index):
    start = time.time() # start the clock
    print("\tProcessing: "+sample) # print which sample is being processed
    data_all = [] # define empty list to hold all data for this sample
    
    # open the tree called mini using a context manager (will automatically close files/resources)
    with uproot.open(path + ":mini") as tree:
        if 'data' not in sample: xsec_weight = get_xsec_weight(sample) # get cross-section weight
        for data in tree.iterate(['lep_pt', 'lep_eta', 'lep_phi', 'lep_E', 'lep_charge', 'lep_type', 
                                  'mcWeight', 'scaleFactor_PILEUP', 'scaleFactor_ELE', 'scaleFactor_MUON', 
                                  'scaleFactor_LepTRIGGER'],
                                  library="ak", entry_start=start_index, entry_stop=end_index):

            nIn = len(data) # number of events in this batch

            if 'data' not in sample: # only do this for Monte Carlo simulation files
                # multiply all Monte Carlo weights and scale factors together to give total weight
                data['totalWeight'] = calc_weight(xsec_weight, data)

            # cut on lepton charge using the function cut_lep_charge defined above
            data = data[~cut_lep_charge(data.lep_charge)]

            # cut on lepton type using the function cut_lep_type defined above
            data = data[~cut_lep_type(data.lep_type)]

            # calculation of 4-lepton invariant mass using the function calc_mllll defined above
            data['mllll'] = calc_mllll(data.lep_pt, data.lep_eta, data.lep_phi, data.lep_E)

            # array contents can be printed at any stage like this
            #print(data)

            # array column can be printed at any stage like this
            #print(data['lep_pt'])

            # multiple array columns can be printed at any stage like this
            #print(data[['lep_pt','lep_eta']])

            nOut = len(data) # number of events passing cuts in this batch
            data_all.append(data) # append array from this batch
            elapsed = time.time() - start # time taken to process
            print("\t\t nIn: "+str(nIn)+",\t nOut: \t"+str(nOut)+"\t in "+str(round(elapsed,1))+"s") # events before and after
    
    return ak.concatenate(data_all) # return array containing events passing all cuts



if __name__ == "__main__":

    # define all the prefixes which appear in the filepaths to their respective sample

    library = {}
    library['data_A'] = "Data/"
    library['data_B'] = "Data/"
    library['data_C'] = "Data/"
    library['data_D'] = "Data/"
    library['Zee'] = "MC/mc_"+str(infofile.infos['Zee']["DSID"])+"."
    library['Zmumu'] = "MC/mc_"+str(infofile.infos['Zmumu']["DSID"])+"."
    library['ttbar_lep'] = "MC/mc_"+str(infofile.infos['ttbar_lep']["DSID"])+"."
    library['llll'] = "MC/mc_"+str(infofile.infos['llll']["DSID"])+"."
    library['ggH125_ZZ4lep'] = "MC/mc_"+str(infofile.infos['ggH125_ZZ4lep']["DSID"])+"."
    library['VBFH125_ZZ4lep'] = "MC/mc_"+str(infofile.infos['VBFH125_ZZ4lep']["DSID"])+"."
    library['WH125_ZZ4lep'] = "MC/mc_"+str(infofile.infos['WH125_ZZ4lep']["DSID"])+"."
    library['ZH125_ZZ4lep'] = "MC/mc_"+str(infofile.infos['ZH125_ZZ4lep']["DSID"])+"."
    
    start = time.time()

    # define environment variables specifying which sample and portion of the indices in that sample \\
    # a particular service is assigned to work through
  
    sample = os.getenv('SAMPLE')
    start_index = int(os.getenv('START_INDEX'))
    end_index = int(os.getenv('END_INDEX'))
    file_path = os.path.join(tuple_path, library[sample] + sample + ".4lep.root")

    processed_data = read_file(file_path, sample, start_index, end_index)

    # Save processed data to a file
    output_filename = f"/app/data/processed-{sample}-{start_index}-{end_index}.awkd"
    ak.to_parquet(processed_data, output_filename)
    elapsed = time.time() - start
    print(f"Time taken: {round(elapsed, 1)}s")
    
