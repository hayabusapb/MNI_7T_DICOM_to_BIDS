from mni_7t_dicom_to_bids.dataclass import BidsDirInfo
from mni_7t_dicom_to_bids.dataset_files import add_dataset_files
from mni_7t_dicom_to_bids.run_dicom_to_niix import check_dicom_to_niix, convert_bids_series
from mni_7t_dicom_to_bids.sort_bids_acquisitions import sort_bids_acquisitions
from mni_7t_dicom_to_bids.sort_dicom_series import sort_dicom_series


def mni_7t_dicom_to_bids(
    input_dicom_dir_path: str,
    output_bids_dir_path: str,
    subject: str,
    session: str,
    overwrite: bool,
):
    print("Checking `dcm2niix` availability...")

    check_dicom_to_niix()

    print("Grouping DICOMs by DICOM series...")

    dicom_series_entries = sort_dicom_series(input_dicom_dir_path)

    print(f"Found {len(dicom_series_entries)} DICOM series:")

    for dicom_series in dicom_series_entries:
        print(
            f"- '{dicom_series.description}\' (series number: {dicom_series.number})'"
            f" ({len(dicom_series.file_paths)} files)"
        )

    print("Mapping DICOM series with BIDS labels...")

    bids_series_entries = sort_bids_acquisitions(dicom_series_entries)

    print(f"Found {len(bids_series_entries)} BIDS acquisitions:")

    for bids_series in bids_series_entries:
        print(
            f"- '{bids_series.scan_type}/{bids_series.file_name}'"
            f" ({len(bids_series.dicom_series)} DICOM series)"
        )

    print('Converting DICOM series to NIfTI...')

    bids_dir = BidsDirInfo(
        path    = output_bids_dir_path,
        subject = subject,
        session = session,
    )

    convert_bids_series(bids_dir, bids_series_entries)

    add_dataset_files(bids_dir, input_dicom_dir_path, overwrite)
