from bic_util.print import print_error_exit
from bic_util.util import find

from mpn_dicom_to_bids.dataclass import BidsAcquisitionInfo, BidsAcquisitionSeriesInfo, DicomSeriesInfo
from mpn_dicom_to_bids.variables import bids_dicom_ignores, bids_dicom_mappings


def sort_bids_acquisitions(dicom_series_entries: list[DicomSeriesInfo]) -> list[BidsAcquisitionSeriesInfo]:
    """
    Sort a set of DICOM series into BIDS acquisitions according to the MPN DICOM to BIDS mapping.
    """

    bids_series_entries: list[BidsAcquisitionSeriesInfo] = []

    for dicom_series in dicom_series_entries:
        if ignore_dicom_series(dicom_series):
            print(f'Ignore DICOM series \'{dicom_series.description}\'')
            continue

        maybe_bids_acquisition = get_bids_acquisition_info(dicom_series)
        if maybe_bids_acquisition is None:
            print_error_exit(f'No BIDS mapping found for DICOM series \'{dicom_series.description}\'')

        bids_acquisition = maybe_bids_acquisition

        bids_series = find(
            lambda bids_series: (
                bids_series.scan_type == bids_acquisition.scan_type
                and bids_series.file_name == bids_acquisition.file_name
            ),
            bids_series_entries,
        )

        if bids_series is None:
            bids_series = BidsAcquisitionSeriesInfo(
                scan_type    = bids_acquisition.scan_type,
                file_name    = bids_acquisition.file_name,
                dicom_series = [],
            )

            bids_series_entries.append(bids_series)

        bids_series.dicom_series.append(dicom_series)

    bids_series_entries.sort(key=lambda bids_series: (bids_series.scan_type, bids_series.scan_type))

    return bids_series_entries


def ignore_dicom_series(dicom_series: DicomSeriesInfo) -> bool:
    """
    Check if a DICOM series should be ignored as per the MPN DICOM to BIDS conversion parameters.
    """

    for bids_dicom_ignore in bids_dicom_ignores:
        if dicom_series.description == bids_dicom_ignore:
            return True

    return False


def get_bids_acquisition_info(dicom_series: DicomSeriesInfo) -> BidsAcquisitionInfo | None:
    """
    Return the BIDS parameters of a DICOM series as per the MPN DICOM to BIDS conversion
    parameters.
    """

    for bids_scan_type, bids_dicom_mapping in bids_dicom_mappings.items():
        for bids_file_name, bids_dicom_series_descriptions in bids_dicom_mapping.items():
            if isinstance(bids_dicom_series_descriptions, str):
                bids_dicom_series_descriptions = [bids_dicom_series_descriptions]

            for bids_dicom_series_description in bids_dicom_series_descriptions:
                if dicom_series.description == bids_dicom_series_description:
                    return BidsAcquisitionInfo(
                        scan_type = bids_scan_type,
                        file_name = bids_file_name,
                    )

    return None
