## Materials Application For EasyVVUQ

Example workflow using [EasyVVUQ](https://easyvvuq.readthedocs.io/en/latest/index.html) to measure the size effect on the Young's modulus of epoxy resin atomistic simulations.

Install [EasyVVUQ](https://easyvvuq.readthedocs.io/en/latest/installation.html) library.

Prepare a template LAMMPS file `in.deform_template`. This file reads in an equilibrated epoxy resin structure and stretches it along all three principal axes to measure its Young's modulus. The location of this file is controlled by the `read_data @source_path/@box_size/@structure_no/@replica_no.data` command. Each variable following an `@` is controlled by EasyVVUQ

Initialise the campaign with `$ python init_campaign.py`. This script contains all the information about which paramters to vary. It creates all the run directories and modifies the LAMMPS input scripts accordingly. 

Add extra runs as desired with `$ python add_runs.py`

In our case we then copied the newly created directory `runs` to a remote computing resource. Execution of all the LAMMPS simulations was handled seperately. Epoxy structures were created using the code documented in [this paper](https://doi.org/10.1002/adts.201800168). The script `calc_ym_lammps.py` was used to calculate the YM for each run, and write to `output.dat`.

Our output is given in `materials_output.tar.gz`. To follow this example through, untar this file and copy it to the location of the EasyVVUQ campaign directory.

Analyse the data using `$ analyse_campaign.py`. This gives the output mentioned in the EasyVVUQ application paper's main text, and the datafile for plotting figure 1. Some of the runs did not complete due to node failures, this is handeled without a problem by pandas.
