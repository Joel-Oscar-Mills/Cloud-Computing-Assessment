# Scaling the HZZ-Analysis from ATLAS with Cloud Technology

The purpose of this processing system is to perform the same data analysis as in the ATLAS notebook (link below), but to 
perform this analysis in a distributed fashion across multiple machines, and be able to configure itself 
automatically, with minimum human intervention.

https://github.com/atlas-outreach-data-tools/notebooks-collection-opendata/blob/master/13-TeV-examples/uproot_python/HZZAnalysis.ipynb

### Required Installation

You'll need to make sure you've installed Docker Desktop (in my case for Mac OS). 
Besides that all other installations as listed in the requirements.txt file. are automated.

### Required Directory Structure
.
├── automation.py
├── data
├── data_processing
│   ├── Dockerfile
│   └── data_processing.py
├── docker-compose.yml
├── infofile.py
├── plotting
│   ├── Dockerfile
│   └── plotting.py
└── requirements.txt

### To Run, Follow these Bash Commands:
