import filecmp
import getpass
import os
import shutil
from datetime import datetime
from importlib.abc import Traversable
from importlib.resources import as_file, files

from bic_util.print import print_error_exit, print_warning

from mpn_dicom_to_bids.dataclass import BidsDirInfo


def add_dataset_files(bids_dir: BidsDirInfo, input_dicom_dir_path: str, overwrite: bool):
    """
    Add the auxiliary dataset files to the output BIDS directory.
    """

    print("Creating auxiliary files...")

    add_static_dataset_files(bids_dir.path, overwrite)

    add_participants_7t_to_bids_json_file(bids_dir, input_dicom_dir_path)

    add_participants_tsv_file(bids_dir)

    add_sessions_tsv_file(bids_dir)


def add_static_dataset_files(bids_dir_path: str, overwrite: bool):
    """
    Copy the static dataset files into the BIDS directory. The files are copied only if they do not
    exist in the BIDS directory, or if they exist and are changed but can be overwritten. Exit the
    program with an error if some file exists and is changed but cannot be overwritten.
    """

    # Copy the static dataset files.
    for file_name in ['.bidsignore', 'README', 'CITATION.cff', 'dataset_description.json', 'participants.json']:
        with as_file(_resolve_asset_file_path(file_name)) as new_file_path:
            old_file_path = os.path.join(bids_dir_path, file_name)

            if not os.path.exists(old_file_path):
                print(f"File '{file_name}' does not exist in the BIDS directory. Creating...")
            else:
                if filecmp.cmp(old_file_path, new_file_path, shallow=False):
                    print(f"File {file_name} already exists in the BIDS directory and is unchanged. Skipping.")
                    continue

                if overwrite:
                    print_warning(
                        f"File '{file_name}' already exists in the BIDS directory and is changed. Overwriting..."
                    )
                else:
                    print_error_exit(
                        f"File '{file_name}' already exists in the BIDS directory and is changed, use the option"
                        " '--overwrite' to overwrite it."
                    )

            shutil.copyfile(new_file_path, old_file_path)

    # Similar logic for task files, which are generated from the template file.
    for task_name in ['cloudy', 'present', 'rest']:
        with as_file(_resolve_asset_file_path('task-template_bold.json')) as task_template_path:
            task_file_name = f'task-{task_name}_bold.json'
            old_task_path = os.path.join(bids_dir_path, task_file_name)
            new_task_path = os.path.join(bids_dir_path, task_file_name)

            with open(task_template_path) as task_template_file:
                new_task = task_template_file.read().replace('TASK_NAME', task_name)

            if not os.path.exists(old_task_path):
                print(f"File '{task_file_name}' does not exist in the BIDS directory. Creating...")
            else:
                with open(old_task_path) as old_task_file:
                    old_task = old_task_file.read()

                if old_task == new_task:
                    print(f"File {task_file_name} already exists in the BIDS directory and is unchanged. Skipping.")
                    continue

                if overwrite:
                    print_warning(
                        f"File '{task_file_name}' already exists in the BIDS directory and is changed. Overwriting..."
                    )
                else:
                    print_error_exit(
                        f"File '{task_file_name}' already exists in the BIDS directory and is changed, use the option"
                        " '--overwrite' to overwrite it."
                    )

            with open(new_task_path, 'w') as new_task_file:
                new_task_file.write(new_task)


def add_participants_7t_to_bids_json_file(bids_dir: BidsDirInfo, input_dicom_dir_path: str):
    """
    Create or update the `participants_7t_to_bids.tsv` file.
    """

    file_path = os.path.join(bids_dir.path, 'participants_7t_to_bids.tsv')
    if os.path.exists(file_path):
        print("File 'participants_7t_to_bids.tsv' already exists.")
    else:
        print("Creating file 'participants_7t_to_bids.tsv'...")
        with open(file_path, 'w') as file:
            file.write("sub\tses\tdate\tN.anat\tN.dwi\tN.func\tN.fmap\tdicoms\tuser\n")

    time = os.path.getmtime(bids_dir.path)
    date_string = datetime.fromtimestamp(time).strftime('%Y-%m-%d')
    anat_count = _count_nifti_files(bids_dir.anat_dir_path)
    dwi_count  = _count_nifti_files(bids_dir.dwi_dir_path)
    func_count = _count_nifti_files(bids_dir.func_dir_path)
    fmap_count = _count_nifti_files(bids_dir.fmap_dir_path)

    print("Appending session to file 'participants_7t_to_bids.tsv'...")

    with open(file_path, 'a') as file:
        file.write(
            f"{bids_dir.subject}\t{bids_dir.session}\t{date_string}\t"
            f"{anat_count}\t{dwi_count}\t{func_count}\t{fmap_count}\t{input_dicom_dir_path}\t{getpass.getuser()}\n"
        )


def add_participants_tsv_file(bids_dir: BidsDirInfo):
    """
    Create or update the `participants.tsv` BIDS file.
    """

    file_path = os.path.join(bids_dir.path, 'participants.tsv')
    if os.path.exists(file_path):
        print("File 'participants.tsv' already exists.")
    else:
        print("Creating file 'participants.tsv'...")
        with open(file_path, 'w') as file:
            file.write("participant_id\tsite\tgroup\n")

    print("Appending session to file 'participants.tsv'...")

    with open(file_path, 'a') as file:
        file.write(f"sub-{bids_dir.subject}\tMontreal_SiemmensTerra7T\tHealthy\n")


def add_sessions_tsv_file(bids_dir: BidsDirInfo):
    """
    Create or update the `sub-XXX_sessions.tsv` BIDS file.
    """

    file_name = f'sub-{bids_dir.subject}_sessions.tsv'
    file_path = os.path.join(bids_dir.subject_dir_path, file_name)

    if os.path.exists(file_path):
        print(f"File '{file_name}' already exists.")
    else:
        print(f"Creating file '{file_name}'...")
        with open(file_path, 'w') as file:
            file.write('session_id\n')

    print(f"Appending session to file '{file_name}'...")

    with open(file_path, 'a') as file:
        file.write(f'ses-{bids_dir.session}\n')


def _resolve_asset_file_path(file_name: str) -> Traversable:
    """
    Resolve a package static asset file path.
    """

    rel_file_path = os.path.join('assets', file_name)
    return files('mpn_dicom_to_bids').joinpath(rel_file_path)


def _count_nifti_files(bids_scan_dir_path: str) -> int:
    """
    Count the NIfTI files in a directory.
    """

    if not os.path.exists(bids_scan_dir_path):
        return 0

    count = 0

    for file in os.scandir(bids_scan_dir_path):
        if file.name.endswith('.nii.gz'):
            count += 1

    return count
