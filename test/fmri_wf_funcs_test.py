#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 15:25:21 2023

@author: costantino_ai
"""

import os, shutil
import pydra
import zipfile
import urllib.request

# Before you proceed, ensure you have installed Pydra and other required packages in your environment:
# pip install pydra pydra-nipype1 mriqc fmriprep

# Function to collect toy data from the dcm2bids tutorial
@pydra.mark.task
@pydra.mark.annotate(
    {
        "root_dir": str,
        "return": {"subs_dir": str, "config_file_path": str},
    }
)
def download_fmri_data_and_config(root_dir: str) -> tuple:
    """
    Download fMRI data and create a configuration file.

    Parameters:
        root_dir: the project's root folder
    Returns:
        tuple: The directory path and configuration file path.
    """

    # Create directories
    source_data_dir = os.path.join(root_dir, "sourcedata")
    os.makedirs(source_data_dir, exist_ok=True)

    tmp_dir = os.path.join(root_dir, "tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    out_dir = os.path.join(source_data_dir, "dcm_qa_nih")

    if not os.path.isdir(out_dir):
        # Download the zipped file
        url = "https://github.com/neurolabusc/dcm_qa_nih/archive/refs/heads/master.zip"
        print(f"STEP: downloading and extracting {url}...", end=" ")
        zip_path = os.path.join(tmp_dir, "dcm_qa_nih-master.zip")
        urllib.request.urlretrieve(url, zip_path)

        # Extract/unzip the zipped file into sourcedata/
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(tmp_dir)

        # Rename zipped folder
        src = os.path.join(tmp_dir, "dcm_qa_nih-master")
        os.rename(src, out_dir)

        print("DONE!")
        
    # Delete temp folder
    shutil.rmtree(tmp_dir)

    # Create the config file
    config_file_path = os.path.join(source_data_dir, "dcm2bids_config.json")
    print(f"STEP: writing config file to {config_file_path}...", end=" ")
    config_content = """{
      "descriptions": [
        {
          "dataType": "func",
          "modalityLabel": "bold",
          "customLabels": "task-rest",
          "criteria": {
            "SeriesDescription": "Axial EPI-FMRI (Interleaved I to S)*"
          },
          "sidecarChanges": {
            "TaskName": "rest"
          }
        },
        {
          "dataType": "fmap",
          "modalityLabel": "epi",
          "customLabels": "dir-AP",
          "criteria": {
            "SeriesDescription": "EPI PE=AP*"
          },
          "intendedFor": 0
        },
        {
          "dataType": "fmap",
          "modalityLabel": "epi",
          "customLabels": "dir-PA",
          "criteria": {
            "SeriesDescription": "EPI PE=PA*"
          },
          "intendedFor": 0
        }
      ]
    }"""

    with open(config_file_path, "w") as config_file:
        config_file.write(config_content)
    print("DONE!")

    subs_dir = os.path.join(out_dir, "In")

    return subs_dir, config_file_path

# BIDS conversion function
def create_dcm2nii_input_spec() -> pydra.specs.SpecInfo:
    """
    Create a Pydra specification for the input parameters of the Dcm2nii command-line tool.
    
    Returns:
    A Pydra SpecInfo object containing the input parameters for the Dcm2nii tool.
    
    Usage:
    Use this function to create a Pydra SpecInfo object that can be used as 
    input to a Pydra Task object for running the Dcm2nii command-line tool. 
    The resulting SpecInfo object contains four input fields: input_dir, 
    participant_id, config_file, and output_dir, which correspond to the 
    input directory, participant ID, configuration file, and output 
    directory parameters of the Dcm2nii tool, respectively.
    """
    return pydra.specs.SpecInfo(
        name="Input",
        fields=[
            (
                "input_dir",
                str,
                {
                    "position": 0,
                    "argstr": "-d {input_dir}",
                    "mandatory": True,
                    "help_string": "The path to the input directory.",
                },
            ),
            (
                "participant_id",
                str,
                {
                    "position": 1,
                    "argstr": "-p {participant_id}",
                    "mandatory": True,
                    "help_string": "The participant ID.",
                },
            ),
            (
                "config_file",
                str,
                {
                    "position": 2,
                    "argstr": "-c {config_file}",
                    "mandatory": True,
                    "help_string": "The path to the configuration file.",
                },
            ),
            (
                "output_dir",
                str,
                {
                    "position": 3,
                    "argstr": "-o {output_dir}",
                    "mandatory": True,
                    "help_string": "The path to the output directory.",
                },
            ),
        ],
        bases=(pydra.specs.ShellSpec,),
    )


@pydra.mark.task
@pydra.mark.annotate(
    {
        "input_dir": str,
        "participant_id": str,
        "config_file": str,
        "root_dir": str,
        "return": {"cmd": pydra.ShellCommandTask},
    }
)
def run_dcm2nii(
    input_dir: str, participant_id: str, config_file: str, root_dir: str
) -> pydra.ShellCommandTask:
    """
    Run dcm2bids using Pydra.

    Parameters:
        input_dir: The path to the input directory.
        participant_id: The participant ID.
        config_file: The path to the configuration file.

    Returns:
        ShellCommandTask: A Pydra ShellCommandTask.
    """
    output_dir = os.path.join(root_dir, "results")
    os.makedirs(output_dir, exist_ok=True)
    
    dcm2nii_input_spec = create_dcm2nii_input_spec()

    dcm2bids = pydra.ShellCommandTask(
        name="dcm2bids",
        executable="dcm2bids",
        input_spec=dcm2nii_input_spec,
        input_dir=input_dir,
        participant_id=participant_id,
        config_file=config_file,
        output_dir=output_dir,
    )
    
    cmd = dcm2bids.cmdline
    print(f"STEP: running the following command-line: \t{cmd}")
    
    return dcm2bids()

# Anonymize and deface function
@pydra.mark.task
def anonymize_and_deface(bids_dir):
    """
    Anonymize and deface NIfTI data using PyDeface.
    """
    # Code to anonymize and deface NIfTI data
    # ...
    return

# MRIQC function
@pydra.mark.task
def run_mriqc(bids_dir, output_dir):
    """
    Run MRIQC and MRIQCeption on the data.
    """
    # Code to perform MRIQC and MRIQCeption
    # ...
    return

# Fmriprep function
@pydra.mark.task
def run_fmriprep(bids_dir, output_dir):
    """
    Preprocess the data using fmriprep.
    """
    # Code to preprocess the data with fmriprep
    # ...
    return

# SPM first-level analysis function
@pydra.mark.task
def run_spm_first_level(bids_dir, output_dir, events_files):
    """
    Run SPM first-level analysis using the information in the event files.
    """
    # Code to perform SPM first-level analysis
    # ...
    return

# Plot results function
@pydra.mark.task
def plot_results(spm_output):
    """
    Plot the results of the SPM first-level analysis.
    """
    # Code to plot the results
    # ...
    return


