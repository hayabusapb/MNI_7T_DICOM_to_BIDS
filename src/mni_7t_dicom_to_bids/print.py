from shlex import quote

from bic_util.print import print_error_exit, print_warning

from mni_7t_dicom_to_bids.dataclass import BidsAcquisitionMapping, DicomSeriesInfo


def print_found_dicom_series(dicom_series_list: list[DicomSeriesInfo]):
    """
    Print the DICOM series found in the DICOM study to the user.
    """

    print(f"Found {len(dicom_series_list)} DICOM series:")

    for dicom_series in dicom_series_list:
        print(
            f"- {quote(dicom_series.description)}"
            f" (series number: {dicom_series.number})"
            f" ({len(dicom_series.file_paths)} files)"
        )


def print_found_bids_acquisition_mappings(bids_acquisition_mappings: list[BidsAcquisitionMapping]):
    """
    Print the BIDS acquisition mappings found in the DICOM study to the user.
    """

    print(f"Found {len(bids_acquisition_mappings)} BIDS acquisitions:")

    for mapping in bids_acquisition_mappings:
        acquisition_name = f"{mapping.acquisition.scan_type}/{mapping.acquisition.file_name}"
        print(
            f"- {quote(acquisition_name)}"
            f" ({len(mapping.dicom_series)} DICOM series)"
        )


def print_found_unknown_dicom_series(
    unknown_dicom_series_list: list[DicomSeriesInfo],
    ignore_unknown: bool,
    convert_unknown: str | None,
):
    """
    Print the unknown DICOM series found in the DICOM study to the user.
    """

    if unknown_dicom_series_list == []:
        return

    dicom_series_count_string = f"Found {len(unknown_dicom_series_list)} unknown DICOM series"

    dicom_series_list_string = "Unknown DICOM series:"
    for dicom_series in unknown_dicom_series_list:
        dicom_series_list_string += (
            "\n"
            f"- {quote(dicom_series.description)}"
            f" (series number: {dicom_series.number})"
            f" ({len(dicom_series.file_paths)} files)"
        )

    match ignore_unknown, convert_unknown:
        case True, _:
            print_warning(
                f"{dicom_series_count_string}, these series will be ignored.\n{dicom_series_list_string}"
            )
        case _, str():
            print_warning(
                f"{dicom_series_count_string}, these series will be converted in '{convert_unknown}'.\n"
                f"{dicom_series_list_string}"
            )
        case _, _:
            print_error_exit(
                f"{dicom_series_count_string}, use option --ignore_unknown or --convert_unknown to proceed"
                f" nonetheless.\n{dicom_series_list_string}"
            )
