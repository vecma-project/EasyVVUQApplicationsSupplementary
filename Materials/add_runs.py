import easyvvuq as uq
import chaospy as cp
import os
import sys
import pytest
from pprint import pprint
import subprocess
import pandas as pd

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


def add_runs(tmpdir):
    # 11. Load state in new campaign object
    print("Reloading campaign...")
    reloaded_campaign = uq.Campaign(state_file="save_state.json", work_dir=tmpdir)
    #reloaded_campaign.collate()
    print(reloaded_campaign)

    sweep = {
        "box_size": [30],
        "structure_no": list(range(1, 11)),
        "replica_no": list(range(1, 11)),
    }

    sampler = uq.sampling.BasicSweep(sweep=sweep)

    # Set the campaign to use this sampler
    reloaded_campaign.set_sampler(sampler)

    # Draw all samples
    reloaded_campaign.draw_samples()
    reloaded_campaign.populate_runs_dir()

    # save campaign state for later read in and analysis
    reloaded_campaign.save_state('save_state2.json')

if __name__ == "__main__":
    add_runs("/tmp/")
