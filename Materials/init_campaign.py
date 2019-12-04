import easyvvuq as uq
from pprint import pprint

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


def init_materials(tmpdir):
    # Set up a fresh campaign called "cannon"
    my_campaign = uq.Campaign(name='materials', work_dir=tmpdir)

    # Define parameter space for the cannonsim app
    params = {
        "box_size": {
            "type": "integer",
            "default": 1,
        },
        "structure_no": {
            "type": "integer",
            "min": 1,
            "max": 11,
            "default": 1,
        },
        "replica_no": {
            "type": "integer",
            "min": 1,
            "max": 11,
            "default": 1,
        },
        "source_path": {
            "type": "string",
            "default": "/path/to/LAMMPS/data/files",
        }
    }

    # Create an encoder, decoder and collater for the cannonsim app
    encoder = uq.encoders.GenericEncoder(
        template_fname='in.deform_template',
        delimiter='@',
        target_filename='in.deform')
    decoder = uq.decoders.SimpleCSV(
        target_filename='out.dat', output_columns=[
            'X', 'Y', 'Z'], header=0)
    collater = uq.collate.AggregateSamples(average=False)

    # Add the cannonsim app
    my_campaign.add_app(name="lammps_box",
                        params=params,
                        encoder=encoder,
                        decoder=decoder,
                        collater=collater)

    # Set the active app to be cannonsim (this is redundant when only one app
    # has been added)
    my_campaign.set_app("lammps_box")

    # Set up samplers
    sweep = {
        "box_size": [40, 60, 80, 100, 150],
        "structure_no": list(range(1, 11)),
        "replica_no": list(range(1, 11)),
    }

    sampler = uq.sampling.BasicSweep(sweep=sweep)

    # Set the campaign to use this sampler
    my_campaign.set_sampler(sampler)

    # Draw all samples
    my_campaign.draw_samples()

    # Print the list of runs now in the campaign db
    print("List of runs added:")
    pprint(my_campaign.list_runs())
    print("---")

    my_campaign.populate_runs_dir()

    # execution handled remotely

    # save campaign state for later read in and analysis
    my_campaign.save_state('save_state.json')


if __name__ == "__main__":
    init_materials("/tmp/")
