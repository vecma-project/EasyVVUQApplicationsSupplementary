# FabUQCampaign 2D ocean model
This tutorial runs 2D ocean model samples from a (local) ![EasyVVUQ](https://github.com/UCL-CCS/EasyVVUQ) campaign using ![FabSim3](https://github.com/djgroen/FabSim3) via the `campaign2ensemble` subroutine. Jobs can be executed locally or be sent to an HPC resource:

![](FabUQMap.png)

## Installation
To install all dependencies, first follow the instructions in https://github.com/wedeling/FabUQCampaign/blob/master/Tutorial_Setup.md

## Explanation of files

+ The `FabUQCampaign` directory contains all files listed below. This directory is located at `<fab_home>/plugins/FabUQCampaign`, where `<fab_home>` is your FabSim3 home directory.

+ `FabUQCampaign/FabUQCampaign.py`: contains the `run_UQ_sample` subroutine in which the job properties are specified, e.g. number of cores, memory, wall-time limit etc.

+ `FabUQCampaign/examples/ocean_2D/*`: an example script, applying EasyVVUQ to a 2D ocean model. See the Detailed Example section below.

+ `FabUQCampaign/templates/ocean`: contains the command-line instruction to draw a single EasyVVUQ sample of the ocean model.

## Dependencies
+ The example below requires EasyVVUQ >= 0.3
+ `FabUQCampaign/examples/ocean_2D/sc/ocean.py` requires ![h5py](https://github.com/h5py/h5py).

## Detailed Examples

### Inputs

+ As noted, the template `FabUQCampaign/template/ocean` contains the command line instruction to run a single sample, in this case: `python3 $ocean_exec ocean_in.json`. Here, `ocean_in.json` is just the input file with the parameter values generated by EasyVVUQ. Furthermore, `$ocean_exec` is the full path to the Python script which runs the advection diffusion equation at the parameters of `ocean_in.json`. It must be specified in `deploy/machines_user.yml`, which in this case looks like
 
`localhost:`

 &nbsp;&nbsp;&nbsp;&nbsp;`ocean_exec: "<fab_home>/plugins/FabUQCampaign/examples/ocean_2D/sc/ocean.py"`

Here, `<fab_home>` is the same directory as specifed above.

### Executing an ensemble job on localhost
In the examples folder the script `examples/ocean_2D/sc/ocean.py` runs an EasyVVUQ Stochastic Collocation (SC) campaign using FabSim3 for a 2D ocean model on a square domain with periodic boundary conditions. Essentially, the governing equations are the Navier-Stokes equations written in terms of the vorticity ![equation](https://latex.codecogs.com/gif.latex?%5Comega) and stream function ![equation](https://latex.codecogs.com/gif.latex?%5CPsi), plus an additional forcing term F:

![equation](https://latex.codecogs.com/gif.latex?%5Cfrac%7B%5Cpartial%5Comega%7D%7B%5Cpartial%20t%7D%20&plus;%20%5Cfrac%7B%5Cpartial%5CPsi%7D%7B%5Cpartial%20x%7D%5Cfrac%7B%5Cpartial%5Comega%7D%7B%5Cpartial%20y%7D%20-%20%5Cfrac%7B%5Cpartial%5CPsi%7D%7B%5Cpartial%20y%7D%5Cfrac%7B%5Cpartial%5Comega%7D%7B%5Cpartial%20x%7D%20%3D%20%7B%5Ccolor%7BRed%7D%20%5Cnu%7D%5Cnabla%5E2%5Comega%20&plus;%20%7B%5Ccolor%7BRed%7D%5Cmu%7D%5Cleft%28F-%5Comega%5Cright%29)

![equation](https://latex.codecogs.com/gif.latex?%5Cnabla%5E2%5CPsi%20%3D%20%5Comega)

The viscosities ![equation](https://latex.codecogs.com/gif.latex?%5Cnu) and ![equation](https://latex.codecogs.com/gif.latex?%5Cmu) are the uncertain parameters. Their values are computed in `ocean.py` by specifying a decay time, which is assigned a user-specified distribution. For illustration purposes, the ocean model just runs for a simulation time of 1 day to limit the runtime of a single sample. This can be easily extended by changing `t_end` in `examples/ocean_2D/sc/ocean.py`.


The first steps are exactly the same as for an EasyVVUQ campaign that does not use FabSim to execute the runs:

 1. Create an EasyVVUQ campaign object: `my_campaign = uq.Campaign(name='sc', work_dir=tmpdir)`
 2. Define the parameter space of the model, comprising of the uncertain parameters `decay_time_nu` and `decay_time_mu`, plus the name of the output file of `ocean.py`:
 
```python
    # Define parameter space
    params = {
        "decay_time_nu": {
            "type": "real",
            "min": "0.0",
            "max": "1000.0",
            "default": "5.0"},
        "decay_time_mu": {
            "type": "real",
            "min": "0.0",
            "max": "1000.0",
            "default": "90.0"},
        "out_file": {
            "type": "str",
            "default": "output.csv"}}
```
2. (continued): the `params` dict corresponds to the template file `examples/ocean_2D/sc/ocean.template`, which defines the input of a single model run. The content of this file is as follows:
```
{"outfile": "$out_file", "decay_time_nu": "$decay_time_nu", "decay_time_mu": "$decay_time_mu"}
```
2. (continued): Select which paramaters of `params` are assigned a Chaospy input distribution, and add these paramaters to the `vary` dict, e.g.:

```python
    vary = {
        "decay_time_nu": cp.Normal(5.0, 0.1),
        "decay_time_mu": cp.Normal(90.0, 1.0)
    }
```

2. (continued) Here, the mean values are the decay times in days.

3. Create an encoder, decoder and collation element. The encoder links the template file to EasyVVUQ and defines the name of the input file (`ocean_in.json`). The model `examples/ocean_2D/sc/ocean.py` writes the total energy (`E`) to a simple `.csv` file, hence we select the `SimpleCSV` decoder, where in this case we have a single output column:
```python
    encoder = uq.encoders.GenericEncoder(
        template_fname = HOME + '/sc/ocean.template',
        delimiter='$',
        target_filename='ocean_in.json')
        
    decoder = uq.decoders.SimpleCSV(target_filename=output_filename,
                                    output_columns=output_columns,
                                    header=0)

    collater = uq.collate.AggregateSamples()
```
3. (continued) `HOME` is the absolute path to the script file. The app is then added to the EasyVVUQ campaign object via
 ```python
     my_campaign.add_app(name="sc",
                        params=params,
                        encoder=encoder,
                        decoder=decoder,
                        collator=collator)
 ```
 
 4. Now we have to select a sampler, in this case we use the SC sampler:
 ```python
     my_sampler = uq.sampling.SCSampler(vary=vary, polynomial_order=3)
     my_campaign.set_sampler(my_sampler)
 ```
 
 4. (continued) If left unspecified, the polynomial order of the SC expansion will be set to 4. 
 
 5. The following commands ensure that we draw all samples, and create the ensemble run directories which will be used in FabSim's `campaign2ensemble` subroutine:
 ```python 
     my_campaign.draw_samples()
     my_campaign.populate_runs_dir()
 ```

6. The only part of the code that changes compared to a EasyVVUQ campaign without FabSim is the job execution, and the retrieval of the results. We use FabSim to run the ensemble via:
 
 ```python
fab.run_uq_ensemble(my_campaign.campaign_dir, script_name='ocean', machine='localhost')
 ```
6. (continued) Here `script_name` refers to the `ocean.template` file. Futhermore, `fab` is a simple FabSim API located in the same directory as the example script. It allows us to run FabSim commands from within a Python environment. Besides submitting the ensemble, `fab` is also used to retrieve the results when the job execution has completed:

```python
fab.get_uq_samples(my_campaign.campaign_dir, machine='localhost')
```

7. Afterwards, post-processing tasks in EasyVVUQ continues in the normal fashion via:
```python
    sc_analysis = uq.analysis.SCAnalysis(sampler=my_sampler, qoi_cols=output_columns)
    my_campaign.apply_analysis(sc_analysis)
    results = my_campaign.get_last_analysis()
```
7. (continued) The `results` dict contains the first 2 statistical moments and Sobol indices for every quantity of interest defined in `output_columns`. If the PCE sampler was used, `SCAnalysis` should be replaced with `PCEAnalysis`.

### Executing an ensemble job on a remote host

To run the example script on a remote host, the `machine` of the remote host must be passed to `fab.run_uq_ensemble`, e.g.:

```python
 fab.run_uq_ensemble(my_campaign.campaign_dir, script_name='ocean', machine='eagle_vecma')
```

Ensure the host is defined in `machines.yml`, and the user login information and `$ocean_exec` in `deploy/machines_user.yml`. For the `eagle` machine, this will look similar to the following:
```
eagle:
 username: "plg<your_username>"
 budget: "vecma2019"
 ocean_exec: "/home/plgrid/plg<your_username>/ocean.py"
```

To automatically setup the ssh keys, and prevent having to login manually for every random sample, run the following from the command line:

```
fab eagle_vecma setup_ssh_keys
```