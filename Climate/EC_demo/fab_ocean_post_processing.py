"""
===============================================================================
SCRIPT FOR POSTPROCESSING THE SAMPLES WHICH WERE EXECUTED IN 
fab_ocean_job_submission.py
===============================================================================
"""

import chaospy as cp
import numpy as np
import easyvvuq as uq
import matplotlib.pyplot as plt
import os
import fabsim3_cmd_api as fab
import pandas as pd
from scipy import stats

# author: Wouter Edeling
__license__ = "LGPL"

#home directory of user
home = os.path.expanduser('~')

def get_kde(X, Npoints = 100):

    kernel = stats.gaussian_kde(X)
    x = np.linspace(np.min(X), np.max(X), Npoints)
    pde = kernel.evaluate(x)
    return x, pde
        
#post processing of UQ samples executed via FabSim. All samples must have been completed
#before this subroutine is executed. Use 'fabsim <machine_name> job_stat' to check their status
def post_proc(state_file, work_dir):
    
    #Reload the campaign
    my_campaign = uq.Campaign(state_file = state_file, work_dir = work_dir)

    print('========================================================')
    print('Reloaded campaign', my_campaign.campaign_dir.split('/')[-1])
    print('========================================================')
    
    #get sampler and output columns from my_campaign object
    my_sampler = my_campaign._active_sampler
    output_columns = my_campaign._active_app_decoder.output_columns
    
    #fetch the results from the (remote) host via FabSim3
    fab.get_uq_samples(my_campaign.campaign_dir, machine='localhost')

    #collate output
    my_campaign.collate()

    # Post-processing analysis
    sc_analysis = uq.analysis.SCAnalysis(sampler=my_sampler, qoi_cols=output_columns)
    my_campaign.apply_analysis(sc_analysis)
    results = my_campaign.get_last_analysis()
    
    return results, sc_analysis, my_sampler, my_campaign

if __name__ == "__main__":
    
    #home dir of this file    
    HOME = os.path.abspath(os.path.dirname(__file__))

    work_dir = "/tmp"

    results, sc_analysis, my_sampler, my_campaign = post_proc(state_file="campaign_state.json", work_dir = work_dir)
    mu_E = results['statistical_moments']['E_mean']['mean']
    std_E = results['statistical_moments']['E_mean']['std']
    mu_Z = results['statistical_moments']['Z_mean']['mean']
    std_Z = results['statistical_moments']['Z_mean']['std']

    print('========================================================')
    print('Mean E =', mu_E)
    print('Std E =', std_E)
    print('Mean Z =', mu_Z)
    print('Std E =', std_Z)
    print('========================================================')
    print('Sobol indices E:')
    print(results['sobols']['E_mean'])
    print(results['sobols']['E_std'])
    print('Sobol indices Z:')
    print(results['sobols']['Z_mean'])
    print(results['sobols']['Z_std'])
    print('========================================================')
    
    #################################
    # Use SC expansion as surrogate #
    #################################
    
    #number of MC samples
    n_mc = 50000
    
    fig = plt.figure()
    ax = fig.add_subplot(111, xlabel=r'$E$', yticks = [])
    
    #get the input distributions
    theta = my_sampler.vary.get_values()
    xi = np.zeros([n_mc, 2])
    idx = 0
    
    #draw random sampler from the input distributions
    print('Sampling surrogate', n_mc, 'times...')
    for theta_i in theta:
        xi[:, idx] = theta_i.sample(n_mc)
        idx += 1
    print('done')
        
    #evaluate the surrogate at the random values
    Q = 'E_mean'
    qoi = np.zeros(n_mc)
    for i in range(n_mc):
        qoi[i] = sc_analysis.surrogate(Q, xi[i])
        
    #plot histogram of surrogate samples
    x, kde = get_kde(qoi)
    plt.plot(x, kde, label=r'$\mathrm{surrogate\;KDE}$')

    #make a list of actual samples
    samples = []
    for i in range(sc_analysis._number_of_samples):
        samples.append(sc_analysis.samples[Q][i])
    
    plt.plot(samples, np.zeros(sc_analysis._number_of_samples), 'ro', label=r'$\mathrm{code\;samples}$')
    
    leg = plt.legend(loc=0)
    plt.ticklabel_format(style='sci', axis='x', scilimits=(0,0))
    leg.set_draggable(True)
    
    plt.tight_layout()
    
plt.show()