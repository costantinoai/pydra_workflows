import os
import nest_asyncio
import pydra

from fmri_wf_funcs import download_fmri_data_and_config, run_dcm2nii

nest_asyncio.apply()

# Make sure you are in project's root folder before running the next line!
project_root_dir = os.getcwd()

# Create a Pydra Workflow with two input_spec parameter: participant_id, out_dir
wf = pydra.Workflow(
    name="fmri2bids", input_spec=["participant_id", "root_dir"]
)

# Set the input_spec value for the workflow
wf.inputs.root_dir = project_root_dir
wf.inputs.participant_id = "01"

# Add the download_fmri_data_and_config task to the workflow
wf.add(
    download_fmri_data_and_config(
        name="download_data",
        root_dir=wf.lzin.root_dir,
    )
)

# Add the run_dcm2nii task to the workflow with Lazy Inputs
# Set the output of the workflow to the output of the run_dcm2nii task
wf.add(
    run_dcm2nii(
        name="dcm2bids",
        input_dir=wf.download_data.lzout.subs_dir,
        participant_id=wf.lzin.participant_id,
        config_file=wf.download_data.lzout.config_file_path,
        root_dir=wf.lzin.root_dir,
    )
)

# Set wf output
wf.set_output(
    {
        "subs_dir": wf.download_data.lzout.subs_dir,
        "config": wf.download_data.lzout.config_file_path,
        "cmd": wf.dcm2bids.lzout.cmd,
    }
)

with pydra.Submitter(plugin="cf") as sub:
    sub(wf)

res = wf.result()
