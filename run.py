#!/usr/bin/env python
"""The run script."""
import logging
import os
from pathlib import Path
from typing import List, Tuple, Union
import nibabel as nib

# import flywheel functions
from flywheel_gear_toolkit import GearToolkitContext

from app.command_line import exec_command
from app.findMatchedScans import find_files
from utils.niftiHeader import pixSize
from utils.demo import get_demo

# The gear is split up into 2 main components. The run.py file which is executed
# when the container runs. The run.py file then imports the rest of the gear as a
# module.

log = logging.getLogger(__name__)

def main(context: GearToolkitContext) -> None:
    """Parses config and runs."""

    subject_label, session_label = get_demo()

    # If one input is given no sub folders are created, so check if these exist, if not run find_files
    if not os.path.exists('/flywheel/v0/input/cor') or not os.path.exists('/flywheel/v0/input/sag'):
        modality = find_files()
    else:
        axial_files = os.listdir('/flywheel/v0/input/axi/')
        axial_file = axial_files[0].upper()
        if 'T1' in axial_file:
            modality = 'T1'
        elif 'T2' in axial_file:
            modality = 'T2'
        else:
            raise RuntimeError(f"Axial input file does not contain T1 or T2: {axial_file}")

    print(f"Modality is: {modality}")

    # Get pixel size from nifti header
    pixdim = pixSize()
    #Get the nifti file under axial input folder ending in .nii or .nii.gz
    input_folder = '/flywheel/v0/input/axi/'
    input_files = [f for f in os.listdir(input_folder) if f.endswith('.nii') or f.endswith('.nii.gz')]
    if not input_files:
        log.error("No NIfTI files found in the axial input folder.")
        return
    
    input = os.path.join(input_folder, input_files[0])
    n1_img = nib.load(input)
    pixdims = (n1_img.header['pixdim'])
    #Get the smallest voxel size as scale factor
    pixdim = min([pixdims[1] ,pixdims[2] , pixdims[3]]) 
    print('Sampling according to smallest voxel size is: ', pixdim)  
    # # Get pixel size from nifti header
    # pixdim = pixSize()

    # Main event
    command = [
        "/flywheel/v0/app/ciso-gear.sh",
        subject_label,
        session_label,
        modality,
        str(pixdim)
    ]

    print(" ".join(command))
    exec_command(
    command,
    shell=False,
    cont_output=True,
    )

# Only execute if file is run as main, not when imported by another module
if __name__ == "__main__":  # pragma: no cover
    # Get access to gear config, inputs, and sdk client if enabled.
    with GearToolkitContext() as gear_context:

        # Initialize logging, set logging level based on `debug` configuration
        # key in gear config.
        gear_context.init_logging()

        # Pass the gear context into main function defined above.
        main(gear_context)