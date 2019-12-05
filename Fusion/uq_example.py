# -*- coding: UTF-8 -*-
import os
import sys
import easyvvuq as uq
from ascii_cpo import read
from templates.xml_encoder import XMLEncoder
from templates.cpo_encoder import CPOEncoder
from templates.cpo_decoder import CPODecoder


# Perform UQ for a fusion workflow using Non intrusive method.
# Uncertainties are driven by:
#  - External sources of Electons heating (3 params).
#  - Electrons boudary condition for Electons Temperature (1 param).
# Quantity of interest: Electrons temperature, Te.


# OS env (The Cluster name, eg.: EAGLE)
SYS = os.environ['SYS']

# Working directory
tmp_dir = "/tmp/"

# CPO files
cpo_dir = os.path.abspath("workflows/AUG_28906_6")

# XML and XSD files
xml_dir = os.path.abspath("workflows")

# The execuatble model code
wobj_dir = os.path.abspath("standalone/bin/"+SYS)
exec_code = "loop_gem0"

# Define a specific parameter space
uncertain_params_bc = {
    # Electrons boudary condition
    "Te_boundary": {
        "type": "float",
        "distribution": "Normal",
        "margin_error": 0.2,
    }
}

uncertain_params_src = {
    # Gaussian Sources: Electrons heating
    "amplitude_el":{
        "type": "float",
        "distribution": "Normal",
        "margin_error": 0.2,
    },
    "position_el":{
        "type": "float",
        "distribution": "Normal",
        "margin_error": 0.2,
    },
    "width_el":{
        "type": "float",
        "distribution": "Normal",
        "margin_error": 0.2,
    }
}

# The Quantitie of intersts
output_columns = ["Te"]

# Initialize Campaign object
campaign_name = "UQ_FUS_"
my_campaign = uq.Campaign(name=campaign_name, work_dir=tmp_dir)

# Create new directory for commons inputs
campaign_dir = my_campaign.campaign_dir
common_dir = campaign_dir +"/common/"
os.system("mkdir " + common_dir)

# Copy XML and XSD files
os.system("cp " + xml_dir + "/ets.x* "    + common_dir)
os.system("cp " + xml_dir + "/chease.x* " + common_dir)
os.system("cp " + xml_dir + "/gem0.x* "   + common_dir)
os.system("cp " + xml_dir + "/source_dummy.x* " + common_dir)

# Copy input CPO files in common directory
os.system("cp " + cpo_dir + "/ets_coreprof_in.cpo "    + common_dir)
os.system("cp " + cpo_dir + "/ets_equilibrium_in.cpo " + common_dir)
os.system("cp " + cpo_dir + "/ets_coreimpur_in.cpo "   + common_dir)
os.system("cp " + cpo_dir + "/ets_coretransp_in.cpo "  + common_dir)
os.system("cp " + cpo_dir + "/ets_toroidfield_in.cpo " + common_dir)

# Create the encoders and get the app parameters
input_cpo_filename = "ets_coreprof_in.cpo"
encoder_cpo = CPOEncoder(template_filename=input_cpo_filename,
                     target_filename=input_cpo_filename,
                     cpo_name="coreprof",
                     common_dir=common_dir,
                     uncertain_params=uncertain_params_bc)

params_cpo, vary_cpo = encoder_cpo.draw_app_params()

input_xml_filename = "source_dummy.xml"
encoder_xml = XMLEncoder(template_filename=input_xml_filename,
                     target_filename=input_xml_filename,
                     common_dir=common_dir,
                     uncertain_params=uncertain_params_src)

params, vary = encoder_xml.draw_app_params()

# Combine both encoders into a single encoder
encoder = uq.encoders.MultiEncoder(encoder_cpo, encoder_xml)
params.update(params_cpo)
vary.update(vary_cpo)

# Create the decoder
output_filename = "ets_coreprof_out.cpo"
decoder = CPODecoder(target_filename=output_filename,
                     cpo_name="coreprof",
                     output_columns=output_columns)

# Create a collation element for this campaign
collater = uq.collate.AggregateSamples(average=False)

# Add the app (automatically set as current app)
my_campaign.add_app(name=campaign_name,
                    params=params,
                    encoder=encoder,
                    decoder=decoder,
                    collater=collater)

# Create the sampler
my_sampler = uq.sampling.PCESampler(vary=vary,
                                    polynomial_order=4,
                                    quadrature_rule='G',
                                    sparse=False)
my_campaign.set_sampler(my_sampler)

# Will draw all (of the finite set of samples)
my_campaign.draw_samples()
my_campaign.populate_runs_dir()

# Run samples
exec_path = os.path.join(obj_dir, exec_code)
my_campaign.apply_for_each_run_dir(uq.actions.ExecuteLocal(exec_path))

# Collate outputs
my_campaign.collate()

# Post-processing analysis
analysis = uq.analysis.PCEAnalysis(sampler=my_sampler, qoi_cols=output_columns)
my_campaign.apply_analysis(analysis)

# Get results
results = my_campaign.get_last_analysis()
