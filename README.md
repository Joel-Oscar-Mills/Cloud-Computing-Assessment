# Scaling the HZZ-Analysis from ATLAS with Cloud Technology

The purpose of this processing system is to perform the same data analysis as in the ATLAS notebook (link below), but to 
perform this analysis in a distributed fashion across multiple machines, and be able to configure itself 
automatically, with minimum human intervention. 

https://github.com/atlas-outreach-data-tools/notebooks-collection-opendata/blob/master/13-TeV-examples/uproot_python/HZZAnalysis.ipynb

### Required Installation

You'll need to make sure you've installed Docker Desktop (in my case for Mac OS). 
Besides that all other installations as listed in the requirements.txt file. are automated.

### Required Directory Structure
. <br>
├── automation.py <br>
├── data <br>
├── data_processing <br>
│   ├── Dockerfile <br>
│   └── data_processing.py <br>
├── docker-compose.yml <br>
├── infofile.py <br>
├── plotting <br>
│   ├── Dockerfile <br>
│   └── plotting.py <br>
└── requirements.txt <br>

### To Run, Follow these Bash Commands:

Firstly, delete any exisiting Docker containers, images, volumes or networks as such (the 2nd command automatically pulls a fresh image from the repo and won't use the cached version that is prebuilt with any parameters you've been using before):

% docker system prune -a
% docker-compose build --no-cache

Then, create a network called "custom_network" to launch all of our containers on:

% docker network create custom_network

Lastly, run the "automation.py" script and specify how many machines should be running computations in parallel (in this case, 100):

% python automation.py 100

