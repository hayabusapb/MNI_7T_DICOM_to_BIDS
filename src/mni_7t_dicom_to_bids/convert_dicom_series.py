import os
import re
import shutil
import subprocess
import tempfile
from collections.abc import Callable
from shlex import quote

from bic_util.print import print_error, print_error_exit, print_warning, with_print_subscript

from mni_7t_dicom_to_bids.dataclass import (
    BidsAcquisitionInfo,
    BidsAcquisitionMapping,
    BidsName,
    BidsSessionInfo,
    DicomSeriesInfo,
)
from mni_7t_dicom_to_bids.post_process import post_process


def check_dicom_to_niix():
    """
    Check that the `dcm2niix` command is accessible, or exit the program with an error if that is
    not the case.
    """

    if shutil.which('dcm2niix') is None:
        print_error_exit(
            "`dcm2niix` does not look installed or accessible on this machine. Please install"
            " `dcm2niix` before running the MNI 7T DICOM to BIDS converter."
        )


def count_bids_acquisitions_conversions(bids_acquisition_mappings: list[BidsAcquisitionMapping]) -> int:
    """
    Get the total number of conversions needed to convert the BIDS acquisitions to NIfTI.
    """

    conversions_total = 0
    for mapping in bids_acquisition_mappings:
        conversions_total += len(mapping.dicom_series)

    return conversions_total


def convert_bids_acquisitions(
    bids_dataset_path: str,
    bids_session: BidsSessionInfo,
    bids_acquisition_mappings: list[BidsAcquisitionMapping],
    overwrite: bool,
):
    """
    Convert the mapped BIDS acquisitions and DICOM series to NIfTI.
    """

    count = 0
    total = count_bids_acquisitions_conversions(bids_acquisition_mappings)

    for mapping in bids_acquisition_mappings:
        for run_number, dicom_series in enumerate(mapping.dicom_series, 1):
            count += 1

            print(
                f"Processing BIDS acquisition '{mapping.acquisition.scan_type}/{mapping.acquisition.file_name}'"
                f" ({count} / {total})."
            )

            if len(mapping.dicom_series) == 1:
                run_number = None

            bids_data_type_path = os.path.join(
                bids_dataset_path,
                f'sub-{bids_session.subject}',
                f'ses-{bids_session.session}',
                mapping.acquisition.scan_type
            )

            os.makedirs(bids_data_type_path, exist_ok=True)

            run_conversion_function(
                dicom_series,
                bids_data_type_path,
                lambda tmp_dicom_dir_path, tmp_output_path: convert_bids_dicom_series(
                    bids_session,
                    mapping.acquisition,
                    bids_data_type_path,
                    run_number,
                    overwrite,
                    tmp_dicom_dir_path,
                    tmp_output_path,
                )
            )


def convert_bids_dicom_series(
    bids_session: BidsSessionInfo,
    bids_acquisition: BidsAcquisitionInfo,
    bids_data_type_path: str,
    run_number: int | None,
    overwrite: bool,
    tmp_dicom_dir_path: str,
    tmp_output_dir_path: str,
):
    """
    Convert an unknown DICOM series to NIfTI.
    """

    file_name = get_bids_acquisition_file_name(bids_session, bids_acquisition.file_name, run_number)

    run_dicom_to_niix(tmp_dicom_dir_path, tmp_output_dir_path, file_name)

    post_process(tmp_output_dir_path)

    # Check if the files already exist in the target directory.
    existing_file_paths: list[str] = []

    for file in os.scandir(tmp_output_dir_path):
        output_file_path = os.path.join(bids_data_type_path, file.name)
        if os.path.exists(output_file_path):
            existing_file_paths.append(output_file_path)

    if existing_file_paths != []:
        existing_files_string = '\n'.join(
            f"- {quote(os.path.relpath(file_path, bids_data_type_path))}"
            for file_path
            in existing_file_paths
        )

        if overwrite:
            print_warning(
                f"Files already present in the BIDS directory, they will be overwritten:\n{existing_files_string}"
            )

            for existing_file_path in existing_file_paths:
                os.remove(existing_file_path)
        else:
            raise Exception(f"Files already exist in directory:\n{existing_files_string}")


def convert_unknown_dicom_series_list(unknown_dicom_series_list: list[DicomSeriesInfo], output_dir_path: str):
    """
    Convert the unknown DICOM series to NIfTI.
    """

    count = 0
    total = len(unknown_dicom_series_list)

    for unknown_dicom_series in unknown_dicom_series_list:
        count += 1

        print(f"Processing unknown DICOM series '{unknown_dicom_series.description}' ({count} / {total}).")

        run_conversion_function(
            unknown_dicom_series,
            output_dir_path,
            lambda tmp_dicom_dir_path, tmp_ouput_dir_path: convert_unknown_dicom_series(
                unknown_dicom_series, tmp_dicom_dir_path, tmp_ouput_dir_path
            ),
        )


def convert_unknown_dicom_series(
    unknown_dicom_series: DicomSeriesInfo,
    tmp_dicom_dir_path: str,
    tmp_output_dir_path: str,
):
    """
    Convert an unknown DICOM series to NIfTI.
    """

    file_name = unknown_dicom_series.description

    # Remove invalid characters.
    file_name = re.sub(r'[^\w\s-]', '', file_name)
    # Replace whitespaces.
    file_name = re.sub(r'[-\s]+', '_', file_name)
    # Prepend series number to disambiguate series runs.
    file_name = f'{unknown_dicom_series.number}_{file_name}'

    run_dicom_to_niix(tmp_dicom_dir_path, tmp_output_dir_path, file_name)


def run_conversion_function(dicom_series: DicomSeriesInfo, output_dir_path: str, convert: Callable[[str, str], None]):
    """
    Run the DICOM to NIfTI conversion function with temporary input and output directories, handle
    file copies, and recover from errors.
    """

    try:
        with tempfile.TemporaryDirectory() as tmp_dicom_dir_path:
            # Copy the DICOM files of the DICOM series in the temporary input directory.
            for dicom_file_path in dicom_series.file_paths:
                shutil.copy(dicom_file_path, tmp_dicom_dir_path)

            with tempfile.TemporaryDirectory() as tmp_output_dir_path:
                convert(tmp_dicom_dir_path, tmp_output_dir_path)

                # Move the output files to their final directory.
                for file in os.scandir(tmp_output_dir_path):
                    shutil.move(file.path, output_dir_path)
    except Exception as error:
        print_error(str(error))


def run_dicom_to_niix(dicom_dir_path: str, output_dir_path: str, file_name: str):
    """
    Run `dcm2niix` on a DICOM series run the post-processings on the result.
    """

    command = [
        'dcm2niix',
        '-z', 'y', '-b', 'y',
        '-o', output_dir_path,
        '-f', file_name,
        dicom_dir_path,
    ]

    print(f"Running dcm2niix with command: '{' '.join(command)}'.")

    process = with_print_subscript(lambda: subprocess.run(command))

    if process.returncode != 0:
        raise Exception(f"dcm2niix exited with code {process.returncode}.")

    print("Generated the following files for this series:")

    for file in os.scandir(output_dir_path):
        print(f"- {quote(file.name)}")


def get_bids_acquisition_file_name(
    bids_session: BidsSessionInfo,
    base_name: str,
    run_number: int | None,
) -> str:
    """
    Get the full BIDS file name of a BIDS acquisition.
    """

    bids_name = BidsName.from_string(base_name)

    # Add the subject and session labels.
    bids_name.add('sub', bids_session.subject)
    bids_name.add('ses', bids_session.session)

    # Add a run number if there are several DICOM series for the BIDS acquisition.
    if run_number is not None:
        bids_name.add('run', str(run_number))

    return str(bids_name)
