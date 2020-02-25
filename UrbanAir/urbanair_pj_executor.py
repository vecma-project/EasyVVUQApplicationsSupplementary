import os
import time

import chaospy as cp
import easyvvuq as uq
import easypj

from emis_encoder import EmisEncoder

from easypj import TaskRequirements, Resources
from easypj import Task, TaskType, SubmitOrder

# author: Michal Kulczewski
__license__ = "LGPL"

# Perform UQ for a UrbanAir application using non intrusive method.
# Uncertainties are driven by input parameters concerning NO2 emission.
# More parameters are to be analyzed in the future

jobdir = os.getcwd()
tmpdir = jobdir
appdir = jobdir

#templates of input data used by app
TEMPLATE = "no2.template"
APPLICATION=os.environ['HOME'] + "/runmpi.sh"
ENCODED_FILENAME = "urbanair_no2.json"
WIND_TEMPLATE = "wind.dat"
SCALARS_TEMPLATE = "scalars.dat"
FORT13_TEMPLATE = "fort.13"
EMIS_TEMPLATE = "emis.dat"



def urbanair_no2_pj(tmpdir):
    tmpdir = str(tmpdir)

    print("Job directory: " + jobdir)
    print("Temporary directory: " + tmpdir)

    # ---- CAMPAIGN INITIALISATION ---
    
    # Set up a UrbanAir campagin - NO2 modelling
    my_campaign = uq.Campaign(name='urbanair_no2', work_dir=tmpdir)

    home=os.environ['HOME']

    # Define parameter space
    params = {
    	"cars": {
        "type": "integer",
        "min": 10,
        "max": 10000,
        "default": 860
    	},
    	"gas_engine": {
        "type": "float",
        "min": 0.1,
        "max": 1.0,
        "default": 0.72
    	},
    	"gas_usage": {
        "type": "float",
        "min": 4.0,
        "max": 13.0,
        "default": 8.0
    	},
    	"gas_density": {
        "type": "float",
        "min": 0.001,
        "max": 0.9,
        "default": 0.75
    	},
    	"gas_no2_index": {
        "type": "float",
        "min": 0.001,
        "max": 1.0,
        "default": 0.00855
    	},
    	"out_file": {
        "type": "string",
        "default": "output.csv"
    	}
		}

    output_filename = params["out_file"]["default"]
    output_columns = ["NO2"]

    # Create encoders, decoder and collation element for UrbanAir
    encoder = uq.encoders.GenericEncoder(
        template_fname=jobdir + '/' + TEMPLATE,
        delimiter='$',
        target_filename=ENCODED_FILENAME)

    wind_encoder = uq.encoders.GenericEncoder(
        template_fname = jobdir + '/' + WIND_TEMPLATE,
        delimiter='$',
        target_filename='wind.dat')

    scalars_encoder = uq.encoders.GenericEncoder(
        template_fname = jobdir + '/' + SCALARS_TEMPLATE,
        delimiter='$',
        target_filename='scalars.dat')
    
    fort13_encoder = uq.encoders.GenericEncoder(
        template_fname = jobdir + '/' + FORT13_TEMPLATE,
        delimiter='$',
        target_filename='fort.13')
    
    emis_encoder = EmisEncoder(
        template_fname = jobdir + '/' + EMIS_TEMPLATE,
        delimiter='$',
        target_filename='emis.dat')

    encoders = uq.encoders.MultiEncoder(encoder, wind_encoder, scalars_encoder,
        fort13_encoder, emis_encoder)

    decoder = uq.decoders.SimpleCSV(target_filename=output_filename,
                                    output_columns=output_columns,
                                    header=0)

    collater = uq.collate.AggregateSamples(average=False)

    # Add the app (automatically set as current app)
    my_campaign.add_app(name="urbanair_no2",
                        params=params,
                        encoder=encoders,
                        decoder=decoder,
                        collater=collater
                        )

    vary = {
        "gas_engine": cp.Uniform(0.1, 0.9),
        "gas_usage": cp.Uniform(3.0, 13.0),
        "gas_density": cp.Uniform(0.001, 0.9),
        "gas_no2_index": cp.Uniform(0.01, 0.1),
    }


    # Create the sampler
    my_sampler = uq.sampling.SCSampler(vary=vary, polynomial_order=1)
    # Associate the sampler with the campaign
    my_campaign.set_sampler(my_sampler)

    # Will draw all (of the finite set of samples)
    my_campaign.draw_samples()

    # use integrator between EasyVVUQ and QCG PilotJob
    qcgpjexec = easypj.Executor()
    # allocate 32 nodes, 24 cores each
    qcgpjexec.create_manager(dir=my_campaign.campaign_dir, resources='32:24')

    # create task to sample parameters. Each task will use 1 core
    # the samples will be generated in parallel
    qcgpjexec.add_task(Task(
        TaskType.ENCODING,
        TaskRequirements(cores=Resources(exact=1))
    ))

    # run the MPI application using 16 nodes, 24 cores each
    # Two ensembles should be run in parallel 
    qcgpjexec.add_task(Task(
        TaskType.EXECUTION,
        TaskRequirements(nodes=Resources(exact=16),cores=Resources(exact=24)),
        application=APPLICATION
    ))

    # first generate samples, then run ensembles
    qcgpjexec.run(
        campaign=my_campaign,
        submit_order=SubmitOrder.PHASE_ORIENTED)

    qcgpjexec.terminate_manager()

    my_campaign.collate()

    sc_analysis = uq.analysis.SCAnalysis(sampler=my_sampler,
                                           qoi_cols=output_columns)
    my_campaign.apply_analysis(sc_analysis)

    results = my_campaign.get_last_analysis()
    stats = results['statistical_moments']['NO2']

    return stats


if __name__ == "__main__":
    start_time = time.time()

    stats = urbanair_no2_pj("/tmp/")

    end_time = time.time()
    print('>>>>> elapsed time = ', end_time - start_time)
