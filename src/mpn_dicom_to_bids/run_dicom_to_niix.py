import os
import shutil
import subprocess
import tempfile

from bic_util.print import print_error_exit

from mpn_dicom_to_bids.dataclass import (
    BidsAcquisitionSeriesInfo,
    BidsDirInfo,
    BidsName,
)
from mpn_dicom_to_bids.post_process import post_process


def check_dicom_to_niix():
    """
    Check that the `dcm2niix` command is accessible, or exit the program with an error if that is
    not the case.
    """

    if shutil.which('dcm2niix') is None:
        print_error_exit(
            "`dcm2niix` does not look installed or accessible on this machine. Please install"
            " `dcm2niix` before running the MPN DICOM to BIDS converter."
        )


def convert_bids_series(
    bids_dir: BidsDirInfo,
    bids_acquisitions: list[BidsAcquisitionSeriesInfo],
):
    """
    Create the NIfTIs for a set of BIDS acquisitions.
    """

    for acquisition_number, bids_acquisition in enumerate(bids_acquisitions, 1):
        for run_number, dicom_series in enumerate(bids_acquisition.dicom_series, 1):
            print(
                f"Processing acquisition '{bids_acquisition.scan_type}/{bids_acquisition.file_name}'"
                f" ({acquisition_number}/{len(bids_acquisitions)}) ({run_number}/{len(bids_acquisition.dicom_series)})"
            )

            with tempfile.TemporaryDirectory() as tmp_dicom_series_dir_path:

                # Copy all DICOMs of the acquisition run a temporary acquisition run directory.
                for dicom_file_path in dicom_series.file_paths:
                    shutil.copy(dicom_file_path, tmp_dicom_series_dir_path)

                bids_file_name = get_bids_acquisition_file_name(bids_dir, bids_acquisition, run_number)

                run_dicom_to_niix(
                    bids_dir,
                    bids_acquisition.scan_type,
                    bids_file_name,
                    tmp_dicom_series_dir_path,
                )


def run_dicom_to_niix(
    bids_dir: BidsDirInfo,
    bids_scan_type: str,
    bids_file_name: str,
    dicom_dir_path: str,
):
    """
    Run the `dcm2niix` command with the provided arguments.
    """

    bids_scan_dir_path = os.path.join(bids_dir.session_dir_path, bids_scan_type)

    os.makedirs(bids_scan_dir_path, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp_acquisition_dir_path:
        command = [
            'dcm2niix',
            '-z', 'y', '-b', 'y',
            '-o', tmp_acquisition_dir_path,
            '-f', bids_file_name,
            dicom_dir_path,
        ]

        print(f"Running dcm2niix with command: '{' '.join(command)}'.")

        subprocess.run(command)

        print("Generated the following files for the acquisition:")

        for file in os.scandir(tmp_acquisition_dir_path):
            print(f"- '{file.name}'")

        post_process(tmp_acquisition_dir_path)

        for file in os.scandir(tmp_acquisition_dir_path):
            shutil.move(file.path, bids_scan_dir_path)


def get_bids_acquisition_file_name(
    bids_dir: BidsDirInfo,
    bids_acquisition: BidsAcquisitionSeriesInfo,
    run_number: int,
) -> str:
    """
    Get the full BIDS file name of a BIDS acquisition.
    """

    bids_name = BidsName.from_string(bids_acquisition.file_name)

    # Add the subject and session labels.
    bids_name.add('sub', bids_dir.subject)
    bids_name.add('ses', bids_dir.session)

    # Add a run number if there are several DICOM series for the BIDS acquisition.
    if len(bids_acquisition.dicom_series) != 1:
        bids_name.add('run', str(run_number))

    return str(bids_name)
