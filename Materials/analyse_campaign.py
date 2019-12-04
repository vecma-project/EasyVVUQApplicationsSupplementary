import easyvvuq as uq
import chaospy as cp
import os
import sys
import pytest
from pprint import pprint
import subprocess
import pandas as pd
import numpy as np

__copyright__ = """

    Copyright 2018 Robin A. Richardson, David W. Wright

    This file is part of EasyVVUQ

    EasyVVUQ is free software: you can redistribute it and/or modify
    it under the terms of the Lesser GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    EasyVVUQ is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    Lesser GNU General Public License for more details.

    You should have received a copy of the Lesser GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
__license__ = "LGPL"

def analyse(campaign):
    # Perform a bootstrap analysis on all the measured YMs grouped by box size
    bootstrap = uq.analysis.EnsembleBoot(groupby=["box_size"],qoi_cols=["Value"])
    campaign.apply_analysis(bootstrap)
    print("bootstrap:\n", campaign.get_last_analysis())
    # Perform basic analysis on the entire campaign
    basicstats = uq.analysis.BasicStats(groupby=["box_size"],qoi_cols=["Value"])
    campaign.apply_analysis(basicstats)
    print("stats:\n", campaign.get_last_analysis())

     # Retrieve the results DataFrame so we can manipulate here
    results = campaign.get_collation_result()[["box_size","structure_no","Value"]]

    total_var                 = results.groupby("box_size").var()["Value"]
    var_per_structure         = results.groupby(["box_size","structure_no"]).var()
    expected_var_given_struct = var_per_structure.groupby("box_size").mean()["Value"]
    var_due_to_structure      = total_var - expected_var_given_struct

    print(pd.concat([total_var.rename('Var(YM)'),
                     expected_var_given_struct.rename('E(Var(YM|structure))'),
                     var_due_to_structure.rename('Var(E(YM|structure))')],
                     axis=1))

def make_files_for_graphs(campaign):
    results = campaign.get_collation_result()

    box_sizes = np.unique(results["box_size"])
    ym_by_size = {size:[] for size in box_sizes}

    violin = {}
    bin_size = 5000
    bins = np.arange(min(results["Value"]),max(results["Value"]),bin_size)

    for size in box_sizes:
        ym_by_size[size] = list(results[results["box_size"] == size]["Value"])
        violin[size] = np.histogram(ym_by_size[size],bins,density=True)[0]

    bins     *= 101325/1e9 # pascal
    bin_size *= 101325/1e9
    max_hist = max(violin[100])

    with open('violin.dat','w') as f:
        for i,line in enumerate(bins[:-1]):
            f.write(str(line+0.5*bin_size)+', ')
            for size in violin:
                if violin[size][i] == 0:
                    f.write(', , ')
                else:
                    x1 = size - violin[size][i] * 10/max_hist
                    x2 = size + violin[size][i] * 10/max_hist
                    x1 /= 10 # nm
                    x2 /= 10
                    f.write(str(x1)+', '+str(x2)+', ')
            f.write('\n')

if __name__ == "__main__":
    # Load state in new campaign object
    print("Reloading campaign...")
    reloaded_campaign = uq.Campaign(state_file="save_state2.json", work_dir="/tmp/")
    reloaded_campaign.collate()
    # Change the format of the results output so all measured YMs are in the one
    # column called 'Value'
    reloaded_campaign.set_collated_dataframe_format('one_row_per_var')

    analyse(reloaded_campaign)
    make_files_for_graphs(reloaded_campaign)

