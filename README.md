# master_thesis

# Master's thesis - Code repository

This repository contains the code for my master's thesis 'Distance estimation in vehicle routing problems: An empirical approach using neural networks and ensemble learning'

Please refer to 'thesis_presentation.pdf' for an overview of the project.

If you have any problems, questions, or suggestions, please contact me at jens.mueller@studbocconi.it


## Abstract

Many transportation and logistics problems require a quick and accurate estimation of routing distances. 
The existing approaches for this task are primarily based on linear regression. 
This thesis studies new models for estimating distances in the Capacitated Vehicle Routing Problem with Time Windows (CVRPTW). 
A multilayer perceptron, a random forest, and a gradient boosting model are implemented. 
To train these models, a dataset of 100,000 CVRPTW instances is generated, including node locations, demands, and time windows from a variety of distributions. 
Distance labels for the dataset are obtained using a guided local search meta-heuristic. 
Next, a large number of features is defined, which the models can extract from a given routing instance to capture information about its characteristics. 
Based on that information, the models can then make a distance prediction. 
Experimental results indicate an improved prediction accuracy by the new models compared to the predominant linear regression approach. 
In particular, the multilayer perceptron and the gradient boosting model achieve good estimates of route distances.


## Repository structure

```
msc_thesis/
│   README.md
│   requirements.txt
|   thesis_presentation.pdf
│
└───data/         ---routing data (download link below)
└───generation/   ---modules for data generation
└───models/       ---distance estimation models
└───notebooks/    ---illustration of the code
└───routing/      ---modules for vehicle routing
```

The full dataset and large models can be downloaded from: 
https://1drv.ms/u/s!As2l-o3xCjvog7ECtHFmfSf3jDecZg?e=ZhO1jL
