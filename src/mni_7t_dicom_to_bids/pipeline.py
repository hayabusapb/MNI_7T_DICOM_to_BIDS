from mni_7t_dicom_to_bids.convert_dicom_series import (
    check_dicom_to_niix,
    convert_bids_acquisitions,
    convert_unknown_dicom_series_list,
)
from mni_7t_dicom_to_bids.dataclass import BidsSessionInfo
from mni_7t_dicom_to_bids.dataset_files import add_dataset_files
from mni_7t_dicom_to_bids.map_bids_dicom_series import map_bids_dicom_series
from mni_7t_dicom_to_bids.print import (
    print_found_bids_acquisition_mappings,
    print_found_dicom_series,
    print_found_unknown_dicom_series,
)
from mni_7t_dicom_to_bids.sort_dicom_series import sort_dicom_series


def mni_7t_dicom_to_bids(
    dicom_study_path: str,
    bids_dataset_path: str,
    subject: str,
    session: str,
    ignore_unknown: bool,
    convert_unknown: str | None,
    dataset_files: bool,
    overwrite: bool,
):
    print("Checking `dcm2niix` availability...")

    check_dicom_to_niix()

    print("Grouping DICOMs by DICOM series...")

    dicom_series_list = sort_dicom_series(dicom_study_path)

    print_found_dicom_series(dicom_series_list)

    bids_acquisition_mappings, unknown_dicom_series = map_bids_dicom_series(
        dicom_series_list,
        ignore_unknown or convert_unknown is not None,
    )

    print_found_bids_acquisition_mappings(bids_acquisition_mappings)

    print_found_unknown_dicom_series(unknown_dicom_series, ignore_unknown, convert_unknown)

    print('Converting DICOM series to NIfTI...')

    bids_session = BidsSessionInfo(
        subject = subject,
        session = session,
    )

    convert_bids_acquisitions(bids_dataset_path, bids_session, bids_acquisition_mappings, overwrite)

    if convert_unknown is not None:
        convert_unknown_dicom_series_list(unknown_dicom_series, convert_unknown)

    if dataset_files:
        add_dataset_files(bids_dataset_path, bids_session, dicom_study_path, overwrite)
