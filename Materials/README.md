
Prepare a template LAMMPS file `in.deform_template`

Initialise the campaign with `$ python init_campaign.py`. This script contains all the information about which paramters to vary. It creates all the run directories and modifies the LAMMPS input scripts accordingly. 

Add extra runs as desired with `$ python add_runs.py`

In our case we then copied the newly created directory `runs` to a remote computing resource. Execution of all the LAMMPS simulations was handled seperately.

Example of the output is given in `materials_output.tar.gz`. To follow this example through, untar this file and copy it to the location of the EasyVVUQ campaign directory.

Analyse the data using `$ analyse_campaign.py`. This gives the output mentioned in the EasyVVUQ application paper's main text, and the datafile for plotting figure 1. Some of the runs did not complete due to node failures, this is handeled without a problem by pandas.
