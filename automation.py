#automation
import subprocess
import sys
import os
import uproot

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Add the directory to sys.path
sys.path.append(script_dir)
import infofile
    

def main(num_workers):  

    tuple_path = "https://atlas-opendata.web.cern.ch/atlas-opendata/samples/2020/4lep/" # web address

    samples = ['data_A', 'data_B', 'data_C', 'data_D',
               'Zee', 'Zmumu', 'ttbar_lep', 'llll',
               'ggH125_ZZ4lep', 'VBFH125_ZZ4lep', 'WH125_ZZ4lep', 'ZH125_ZZ4lep']
        
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

        
    with open("./data/num_workers.txt", "w") as f:
        f.write(str(num_workers))                

    for sample in samples:
    
        processes = []

        path = os.path.join(tuple_path, library[sample] + sample + ".4lep.root")
        with uproot.open(path + ":mini") as tree:
            total_entries = tree.num_entries # number of events
        chunk_size = total_entries // num_workers
                
        for i in range(num_workers):

            start_index = i * chunk_size
            end_index = start_index + chunk_size 
            if i == num_workers - 1:
                end_index = total_entries

            process = subprocess.Popen(["docker-compose", "run", "--rm", "-e", f"SAMPLE={sample}", 
                            "-e", f"START_INDEX={start_index}", "-e", f"END_INDEX={end_index}", 
                            "data_processing"])
    
            processes.append(process)

        # Run the plotting process after all data processing is done
        for process in processes:
            process.wait()
        
    
    subprocess.run(["docker-compose", "run", "--rm", "plotting"])


if __name__ == "__main__":

    if int(len(sys.argv)) == 2:
        PROGNAME = sys.argv[0]
        NUMWORKERS = int(sys.argv[1])
    else:
        print("Usage: python {} <NUMWORKERS>".format(sys.argv[0]))

    main(NUMWORKERS)