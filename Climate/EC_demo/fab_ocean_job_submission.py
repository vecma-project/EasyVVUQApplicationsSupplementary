"""
===============================================================================
SCRIPT FOR SUBMITTING AN EASYVUQ ENSEMBLE OF A SIMPLIFIED 2D OCEAN MODEL
-------------------------------------------------------------------------------
FOR ILLUSTRATION PURPOSES: 
    - SAMPLES ARE RUN ON THE LOCALHOST
    - SAMPLES ARE INTEGRATED IN TIME ONLY FOR A SMALL TIME PERIOD
    
SEE TUTORIAL FOR THE SETUP OF FABSIM3
===============================================================================
"""

import chaospy as cp
import numpy as np
import easyvvuq as uq
import matplotlib.pyplot as plt
import os
import fabsim3_cmd_api as fab
import tkinter as tk
from tkinter import filedialog

# author: Wouter Edeling
__license__ = "LGPL"

#Create EasyVVUQ Campaign and submit the jobs via FabSim3
def run_sc_samples(work_dir):
    
    # Set up a fresh campaign called "sc"
    my_campaign = uq.Campaign(name='ocean', work_dir=work_dir)

    # Define parameter space
    params = {
        "decay_time_nu": {
            "type": "float",
            "min": 0.0,
            "max": 1000.0,
            "default": 5.0},
        "decay_time_mu": {
            "type": "float",
            "min": 0.0,
            "max": 1000.0,
            "default": 90.0},
        "out_file": {
            "type": "string",
            "default": "output.csv"}}

    output_filename = params["out_file"]["default"]
    output_columns = ["E_mean", "Z_mean", "E_std", "Z_std"]

    # Create an encoder, decoder and collation element for PCE test app
    encoder = uq.encoders.GenericEncoder(
        template_fname= HOME + '/sc/ocean.template',
        delimiter='$',
        target_filename='ocean_in.json')
    decoder = uq.decoders.SimpleCSV(target_filename=output_filename,
                                    output_columns=output_columns,
                                    header=0)
    collater = uq.collate.AggregateSamples(average=False)

    # Add the SC app (automatically set as current app)
    my_campaign.add_app(name="sc",
                        params=params,
                        encoder=encoder,
                        decoder=decoder,
                        collater=collater)    

    # Specify the uncertain input distibutions
    vary = {
        "decay_time_nu": cp.Normal(5.0, 1.0),     #decay time of nu in days
        "decay_time_mu": cp.Uniform(80.0, 90.0)    #decay time of mu in days
    }

    my_sampler = uq.sampling.SCSampler(vary=vary, polynomial_order=1)
    # Associate the sampler with the campaign
    my_campaign.set_sampler(my_sampler)
    
    # Will draw all (of the finite set of samples)
    my_campaign.draw_samples()

    my_campaign.populate_runs_dir()
    
    fig = plt.figure()
    ax = fig.add_subplot(111)
    xi_d = my_sampler.xi_d
    ax.plot(xi_d[:,0], xi_d[:, 1], 'ro')
    plt.tight_layout()
    plt.pause(0.1)

    #Run execution using Fabsim 
    # fab.run_uq_ensemble(my_campaign.campaign_dir, 'ocean', machine='eagle_vecma')
    fab.run_uq_ensemble(my_campaign.campaign_dir, 'ocean', machine='localhost')
    
    #Save the Campaign
    my_campaign.save_state("campaign_state.json")
    
if __name__ == "__main__":
    
    #home dir of this file    
    HOME = os.path.abspath(os.path.dirname(__file__))
    
    work_dir = "/tmp"

    #perform the EasyVVUQ steps up to sampling
    run_sc_samples(work_dir)