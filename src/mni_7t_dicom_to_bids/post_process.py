import json
import math
import os
from pathlib import Path

from bic_util.fs import rename_file

from mni_7t_dicom_to_bids.dataclass import BidsName


def post_process(acquisition_path: str):
    for file_name in os.scandir(acquisition_path):
        file_path = os.path.join(acquisition_path, file_name)
        post_process_file(file_path)

    post_process_json(acquisition_path)


def post_process_file(file_path: str):
    """
    Apply MNI 7T BIDS post processing.
    """

    file_name = os.path.basename(file_path)
    bids_name = BidsName.from_string(file_name)

    # Delete the bval and bvec files from MP2RAGE acquisitions.
    if bids_name.has('MP2RAGE') and (bids_name.extension == 'bval' or bids_name.extension == 'bvec'):
        print(f"Remove MP2RAGE bval/bvec file '{file_name}'")
        os.remove(file_path)
        return

    # Delete the 'ROI1' files.
    if bids_name.has('ROI1'):
        print(f"Remove ROI file '{file_name}'")
        os.remove(file_path)
        return

    # Replace 'e?' by 'echo-?'
    echo_match = bids_name.match(r'e(\d)')
    if echo_match is not None:
        bids_name.remove(echo_match.group(0))
        bids_name.add('echo', echo_match.group(1))

    # Remove 'run-?' from echo files (there can be several 'task-rest' runs per acquisition).
    if bids_name.has('echo') and bids_name.has('run') and not bids_name.has_value('task', 'rest'):
        bids_name.remove('run')

    # Remove 'run-?' from MTR files.
    if bids_name.has_value('acq', 'mtw') and bids_name.has('run'):
        bids_name.remove('run')

    # Replace 'ph' with 'part-phase'.
    if bids_name.has('ph'):
        bids_name.remove('ph')
        bids_name.add('part', 'phase')

    # Add 'part-mag' to T2 files with echo
    if bids_name.has('T2starw') and bids_name.has('echo') and not bids_name.has('part'):
        bids_name.add('part', 'mag')

    # Replace standalone 'T2starw' with 'T2starmap'.
    if (bids_name.has_value('acq', 'aspire') and bids_name.has('T2starw')
        and not bids_name.has('desc') and not bids_name.has('part')
    ):
        bids_name.remove('run')
        bids_name.remove('T2starw')
        bids_name.add('T2starmap')

    # Remove 'run-1' in 7T DWI acquisitions.
    if bids_name.has('dwi') and bids_name.has_value('run', '1'):
        bids_name.remove('run')

    # Replace 'run-2' with 'part-phase' in 7T DWI acquisitions.
    if bids_name.has('dwi') and bids_name.has_value('run', '2'):
        bids_name.remove('run')
        bids_name.add('part', 'phase')

    # Apply the TB1TFL-specific post processing.
    if bids_name.has('TB1TFL'):
        run_number = int(bids_name.get('run') or 0)
        acquisition_name = 'anat' if run_number % 2 == 1 else 'sfam'
        bids_name.add('acq', acquisition_name)
        bids_name.add('run', str(math.ceil(run_number / 2)))

    new_file_name = str(bids_name)

    # Rename the file on the system.
    if new_file_name != file_name:
        print(f"Renaming '{file_name}' to '{new_file_name}'.")
        rename_file(file_path, new_file_name)


def post_process_json(acquisition_path: str):
    """
    Patch the generated BIDS JSON sidercar files with additional information.
    """

    # Add 'Units' to 'part-phase' scans.
    phase_paths = Path(acquisition_path).rglob('*part-phase*.json')
    for phase_path in phase_paths:
        with open(phase_path) as phase_file:
            data = json.load(phase_file)

        data['Units'] = 'rad'

        with open(phase_path, 'w') as phase_file:
            json.dump(data, phase_file, indent=4)

    # Add 'MTState' to 'mt-off' scans.
    for mt_off_path in Path(acquisition_path).rglob('*mt-off*.json'):
        with open(mt_off_path) as mt_off_file:
            data = json.load(mt_off_file)

        data['MTState'] = False

        with open(mt_off_path, 'w') as mt_off_file:
            json.dump(data, mt_off_file, indent=4)

    # Add 'MTState' to 'mt-on' scans.
    for mt_on_path in Path(acquisition_path).rglob('*mt-on*.json'):
        with open(mt_on_path) as mt_on_file:
            data = json.load(mt_on_file)

        data['MTState'] = True

        with open(mt_on_path, 'w') as mt_on_file:
            json.dump(data, mt_on_file, indent=4)
